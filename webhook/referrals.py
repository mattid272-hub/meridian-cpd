"""Refer a colleague: a personal code for every annual subscriber.

How it works
  - Every live annual subscriber gets a personal Stripe promotion code (made the first
    time they open My CPD → Refer a colleague) on one coupon Matt creates in Stripe:
    £10 off once, restricted to the annual subscription product, so the code is refused
    at checkout on a single course, a series or the free course. The code's metadata
    names the member, and the member row keeps the code and its Stripe id.
  - The share link is APP_URL/r/<code>: a short page that sends the colleague to the
    annual Payment Link with the code filled in (?prefilled_promo_code=). The code can
    also be typed at checkout.
  - When a checkout that used a referral code completes and is paid, on_checkout()
    records it in the referrals table (one row per checkout, so a repeat delivery of the
    event does nothing) and puts £10 of credit on the referrer's Stripe customer balance,
    which Stripe takes off their next invoice, i.e. their renewal. Credit held is capped
    at the referrer's renewal price (a free year); a referral past the cap is recorded as
    "capped" with no credit.
  - No credit for: the referrer's own checkout, someone who has subscribed before, a
    person already referred, or a checkout that is not an annual subscription.

The whole scheme is off until REFERRAL_COUPON_ID is set (Railway). Nothing here changes
a price, a coupon or a Payment Link: it makes promotion codes on Matt's coupon and adds
customer-balance credit, both only once he has set the coupon up and the variable.
"""
from __future__ import annotations

import os
import re
import secrets

import stripe

CREDIT_PENCE = 1000                     # £10, for the referrer and (via the coupon) the newcomer
FALLBACK_RENEWAL_PENCE = 7900           # cap if the referrer's renewal price cannot be read
DEFAULT_SUBSCRIPTION_LINK = "https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01"
_SUFFIX_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"   # no 0/O, 1/I/L
_CODE_RE = re.compile(r"^[A-Z0-9-]{4,24}$")

# Referral statuses (referrals.status)
CREDITED = "credited"                   # £ credit added to the referrer's balance
CAPPED = "capped"                       # referrer already holds a free year of credit
SELF = "refused_self"                   # the referrer used their own code
EXISTING = "refused_existing"           # the newcomer had subscribed before
DUPLICATE = "refused_duplicate"         # this person was already referred
NOT_SUBSCRIPTION = "refused_not_subscription"
NO_CUSTOMER = "pending_no_customer"     # referrer has no Stripe customer id on file
FAILED = "credit_failed"                # Stripe refused the credit; retried on the next delivery
COUNTED = (CREDITED, CAPPED)            # successful referrals, shown to the referrer


def enabled() -> bool:
    return bool(coupon_id())


def coupon_id() -> str:
    return os.environ.get("REFERRAL_COUPON_ID", "").strip()


def subscription_link() -> str:
    return (os.environ.get("STRIPE_SUBSCRIPTION_LINK", "").strip() or DEFAULT_SUBSCRIPTION_LINK)


def _g(obj, key, default=None):
    if obj is None:
        return default
    try:
        v = obj.get(key, default)
    except AttributeError:
        v = getattr(obj, key, default)
    return default if v is None else v


def _id(v) -> str:
    if v and not isinstance(v, str):
        v = _g(v, "id", "")
    return v or ""


def normalise_code(code: str) -> str:
    code = (code or "").strip().upper()
    return code if _CODE_RE.match(code) else ""


def first_name(name: str) -> str:
    """First word of a member's name, for the referrer's list. Never the surname or email."""
    word = (name or "").strip().split(" ")[0] if (name or "").strip() else ""
    return "" if "@" in word else word[:30]


def _new_code(name: str) -> str:
    stem = re.sub(r"[^A-Z]", "", first_name(name).upper())[:8] or "MERIDIAN"
    return f"{stem}-{''.join(secrets.choice(_SUFFIX_ALPHABET) for _ in range(4))}"


def ensure_code(db, member: dict) -> str:
    """The member's referral code, made in Stripe the first time. '' if the scheme is off
    or Stripe would not make one (the page then says the code is not ready)."""
    if member.get("referral_code") and member.get("referral_promo_id"):
        return member["referral_code"]
    if not enabled():
        return ""
    last = None
    for _ in range(3):  # a clash with an existing code is retried with a new suffix
        code = _new_code(member.get("name", ""))
        try:
            promo = stripe.PromotionCode.create(
                promotion={"type": "coupon", "coupon": coupon_id()},
                code=code,
                restrictions={"first_time_transaction": True},
                metadata={"purpose": "referral", "member_id": str(member["id"])},
            )
        except stripe.error.InvalidRequestError as e:
            last = e
            continue
        except stripe.error.StripeError as e:
            print(f"ACTION NEEDED: could not make a referral code for member {member['id']}: {e}")
            return ""
        promo_id = _id(promo)
        res = db.table("members").update({"referral_code": code, "referral_promo_id": promo_id}).eq(
            "id", member["id"]).is_("referral_code", "null").execute()
        if not res.data:
            # Another request got there first; its code stands. This promotion code still
            # names the member in its metadata, so a checkout that somehow used it is still
            # credited (see _referrer_for_promo).
            again = db.table("members").select("referral_code").eq("id", member["id"]).execute().data or []
            return (again[0].get("referral_code") or "") if again else ""
        member["referral_code"], member["referral_promo_id"] = code, promo_id
        return code
    print(f"ACTION NEEDED: could not make a referral code for member {member['id']}: {last}")
    return ""


def referrer_by_code(db, code: str) -> dict | None:
    code = normalise_code(code)
    if not code:
        return None
    rows = db.table("members").select("*").eq("referral_code", code).execute().data or []
    return rows[0] if rows else None


def _promo_ids_used(session) -> list[str]:
    ids = [_id(_g(d, "promotion_code")) for d in (_g(session, "discounts", []) or [])]
    ids = [i for i in ids if i]
    if ids:
        return ids
    # Older event shapes carry the discount only in the expanded totals.
    sid = _g(session, "id", "")
    if not sid:
        return []
    full = stripe.checkout.Session.retrieve(sid, expand=["total_details.breakdown"])
    found = []
    for d in _g(_g(_g(full, "total_details", {}), "breakdown", {}), "discounts", []) or []:
        pid = _id(_g(_g(d, "discount", {}), "promotion_code"))
        if pid:
            found.append(pid)
    return found


def _referrer_for_promo(db, promo_id: str) -> dict | None:
    rows = db.table("members").select("*").eq("referral_promo_id", promo_id).execute().data or []
    if rows:
        return rows[0]
    promo = stripe.PromotionCode.retrieve(promo_id)
    meta = _g(promo, "metadata", {}) or {}
    if _g(meta, "purpose") != "referral" or not _g(meta, "member_id"):
        return None   # some other code, e.g. MERIDIAN10
    rows = db.table("members").select("*").eq("id", _g(meta, "member_id")).execute().data or []
    return rows[0] if rows else None


def renewal_pence(customer_id: str) -> int:
    """What the referrer's next renewal costs: the cap on the credit they can hold."""
    try:
        subs = stripe.Subscription.list(customer=customer_id, status="all", limit=5)
        for sub in _g(subs, "data", []) or []:
            if _g(sub, "status") in ("active", "trialing", "past_due"):
                amounts = [_g(_g(i, "price", {}), "unit_amount") for i in _g(_g(sub, "items", {}), "data", []) or []]
                total = sum(a for a in amounts if a)
                if total:
                    return int(total)
    except stripe.error.StripeError as e:
        print(f"Referral: could not read the renewal price for {customer_id}: {e}")
    return FALLBACK_RENEWAL_PENCE


def credit_held_pence(customer_id: str) -> int | None:
    """Credit on the customer's Stripe balance (a negative balance is credit). None if unreadable."""
    if not customer_id:
        return 0
    try:
        bal = _g(stripe.Customer.retrieve(customer_id), "balance", 0) or 0
    except stripe.error.StripeError as e:
        print(f"Referral: could not read the balance for {customer_id}: {e}")
        return None
    return max(0, -int(bal))


def _credit(db, row: dict, referrer: dict, session_id: str) -> None:
    customer_id = referrer.get("stripe_customer_id") or ""
    if not customer_id:
        db.table("referrals").update({"status": NO_CUSTOMER}).eq("id", row["id"]).execute()
        print(f"ACTION NEEDED: referral {session_id}: referrer {referrer['id']} has no Stripe customer "
              f"on file, so no credit was added. Add £10 to their balance in Stripe by hand.")
        return
    held = credit_held_pence(customer_id)
    if held is None:
        db.table("referrals").update({"status": FAILED}).eq("id", row["id"]).execute()
        raise RetryLater(f"referral {session_id}: balance unreadable")
    amount = min(CREDIT_PENCE, renewal_pence(customer_id) - held)
    if amount <= 0:
        db.table("referrals").update({"status": CAPPED, "credit_pence": 0}).eq("id", row["id"]).execute()
        print(f"Referral {session_id}: referrer {referrer['id']} already holds a free year of credit; recorded, no credit.")
        return
    try:
        txn = stripe.Customer.create_balance_transaction(
            customer_id, amount=-amount, currency="gbp",
            description="Referral credit, Meridian CPD",
            metadata={"purpose": "referral", "checkout_session": session_id},
            idempotency_key=f"referral-credit-{session_id}",
        )
    except stripe.error.StripeError as e:
        db.table("referrals").update({"status": FAILED}).eq("id", row["id"]).execute()
        raise RetryLater(f"referral {session_id}: credit refused by Stripe: {e}") from e
    db.table("referrals").update({"status": CREDITED, "credit_pence": amount,
                                  "credit_txn_id": _id(txn)}).eq("id", row["id"]).execute()
    print(f"Referral {session_id}: £{amount / 100:g} credit for member {referrer['id']}")


class RetryLater(RuntimeError):
    """The credit could not be added; the webhook answers 500 so Stripe delivers the event
    again (the order itself is already recorded, and a repeat delivery does not re-send it)."""


def on_checkout(db, session) -> str | None:
    """Record and credit a referral for one completed checkout. Returns the referral status,
    or None if the checkout used no referral code. Raises RetryLater only when the credit
    could not be added and a retry may succeed; anything else prints ACTION NEEDED."""
    session_id = _g(session, "id", "")
    try:
        if not enabled() or not session_id:
            return None
        promo_ids = _promo_ids_used(session)
        referrer = None
        promo_id = ""
        for pid in promo_ids:
            referrer = _referrer_for_promo(db, pid)
            if referrer:
                promo_id = pid
                break
        if not referrer:
            return None

        existing = db.table("referrals").select("*").eq("stripe_session_id", session_id).execute().data or []
        if existing:
            row = existing[0]
            if row.get("status") in (FAILED, "crediting"):
                _credit(db, row, referrer, session_id)
                row = (db.table("referrals").select("*").eq("id", row["id"]).execute().data or [row])[0]
            return row.get("status")

        email = str(_g(_g(session, "customer_details", {}), "email", "") or "").strip().lower()
        customer_id = _id(_g(session, "customer"))
        newcomer = None
        if email:
            rows = db.table("members").select("*").eq("email", email).execute().data or []
            newcomer = rows[0] if rows else None
        newcomer_id = (newcomer or {}).get("id")

        if _g(session, "mode") != "subscription" or _g(session, "payment_status") != "paid":
            status = NOT_SUBSCRIPTION
        elif (newcomer_id and newcomer_id == referrer["id"]) or (email and email == (referrer.get("email") or "").lower()) \
                or (customer_id and customer_id == referrer.get("stripe_customer_id")):
            status = SELF
        elif newcomer_id and (db.table("referrals").select("id").eq("referred_member_id", newcomer_id)
                              .in_("status", list(COUNTED)).execute().data):
            status = DUPLICATE
        elif newcomer_id and any(p.get("stripe_session_id") != session_id for p in (
                db.table("purchases").select("stripe_session_id").eq("member_id", newcomer_id)
                .eq("course_id", "SUBSCRIPTION").execute().data or [])):
            status = EXISTING
        else:
            status = "crediting"

        row = db.table("referrals").insert({
            "referrer_member_id": referrer["id"],
            "referred_member_id": newcomer_id,
            "stripe_session_id": session_id,
            "promotion_code_id": promo_id,
            "code": referrer.get("referral_code") or "",
            "amount_paid_pence": int(_g(session, "amount_total", 0) or 0),
            "status": status,
        }).execute().data[0]
        if status != "crediting":
            print(f"ACTION NEEDED: referral code {referrer.get('referral_code')} used on checkout {session_id} "
                  f"({status}); no credit added. The newcomer still had the discount: check in Stripe.")
            return status
        _credit(db, row, referrer, session_id)
        got = db.table("referrals").select("status").eq("id", row["id"]).execute().data or [{}]
        return got[0].get("status")
    except RetryLater as e:
        print(f"ACTION NEEDED: {e}. Stripe will deliver the event again; if it keeps failing, add "
              f"the £10 credit to the referrer's balance in Stripe by hand.")
        raise
    except Exception as e:
        print(f"ACTION NEEDED: referral handling for checkout {session_id} failed: {e}. "
              f"It is retried when Stripe delivers the event again; if it keeps failing, add the "
              f"£10 credit to the referrer's balance in Stripe by hand.")
        return None


def referred_by(db, member_id) -> list[dict]:
    """The referrer's successful referrals, oldest first: [{first_name, status, credit_pence}]."""
    rows = db.table("referrals").select("*").eq("referrer_member_id", member_id).in_(
        "status", list(COUNTED)).order("created_at").execute().data or []
    ids = [r["referred_member_id"] for r in rows if r.get("referred_member_id")]
    names = {}
    if ids:
        for m in db.table("members").select("id, name").in_("id", ids).execute().data or []:
            names[m["id"]] = first_name(m.get("name", ""))
    return [{"first_name": names.get(r.get("referred_member_id")) or "A colleague",
             "status": r.get("status"), "credit_pence": int(r.get("credit_pence") or 0)} for r in rows]
