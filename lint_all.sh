#!/bin/bash

echo "Running comprehensive linting for all files..."
echo "==========================================="

# Backend Python linting
echo ""
echo "Backend Python Linting (flake8):"
echo "---------------------------------"
flake8 . --count --statistics

# Frontend JavaScript/JSX linting
echo ""
echo "Frontend JavaScript/JSX Linting (ESLint):"
echo "------------------------------------------"
cd /Users/damondecrescenzo/tilores_X/dashboard && npx eslint src/ --ext .js,.jsx,.mjs

echo ""
echo "Linting complete!"
