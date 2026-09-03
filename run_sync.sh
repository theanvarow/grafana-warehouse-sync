#!/bin/bash
cd "/Users/this/Desktop/Graffana conect with table" || exit 1
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
exec /opt/homebrew/bin/python3 auto_sync_all.py 60
