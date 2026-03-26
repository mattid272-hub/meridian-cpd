#!/bin/bash
# Meridian CPD — Start Admin Portal
# Double-click this file to launch the admin portal in your browser

cd "$(dirname "$0")"
echo "Starting Meridian CPD Admin Portal..."
echo "Open your browser at: http://localhost:8080/admin/"
echo "Press Ctrl+C to stop."
open "http://localhost:8080/admin/"
python3 -m http.server 8080
