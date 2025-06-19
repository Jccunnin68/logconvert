#!/usr/bin/env python
"""
Test script to verify imports work correctly
"""

print("Testing imports...")

try:
    from log_converter import ContentProcessor, get_wikitext_from_url, process_file, WIKI_API_URL
    print("✓ Successfully imported from log_converter")
    print(f"✓ WIKI_API_URL: {WIKI_API_URL}")
    
    # Test creating processor
    processor = ContentProcessor()
    print("✓ Successfully created ContentProcessor")
    
    # Test processing a simple file
    result = process_file("test_log.txt")
    if result:
        title, content = result
        print(f"✓ Successfully read test file - Title: {title}, Content length: {len(content)}")
        
        # Test processing
        processed = processor.process_log_content(title, content)
        print(f"✓ Successfully processed content - Output length: {len(processed)}")
        print("First 200 characters of output:")
        print(processed[:200])
    else:
        print("✗ Failed to read test file")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Other error: {e}")
    import traceback
    traceback.print_exc()

print("Test complete!") 