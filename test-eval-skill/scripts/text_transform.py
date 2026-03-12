#!/usr/bin/env python3
"""
Simple text transformation script for test-eval-skill
"""

import sys
import argparse

def transform_text(text, operation):
    if operation == "uppercase":
        return text.upper()
    elif operation == "reverse":
        return text[::-1]
    elif operation == "count":
        return str(len(text))
    else:
        return f"Unknown operation: {operation}"

def main():
    parser = argparse.ArgumentParser(description='Text transformation utility')
    parser.add_argument('text', help='Input text to transform')
    parser.add_argument('operation', help='Transformation operation (uppercase, reverse, count)')

    args = parser.parse_args()

    result = transform_text(args.text, args.operation)
    print(result)

if __name__ == "__main__":
    main()