"""
Flow Controller
Runs extract, upload, and analyze scripts in sequence
Usage: python flow.py [--all | --extract | --upload | --analyze]
"""

import sys
import subprocess

def run_script(script_name):
    """Run a Python script and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print(f"{'='*60}\n")
    
    result = subprocess.run(['python', script_name], capture_output=False)
    
    if result.returncode != 0:
        print(f"\n {script_name} failed with exit code {result.returncode}")
        sys.exit(1)
    
    print(f"\n {script_name} completed successfully")

def main():
    if len(sys.argv) < 2:
        print("Usage: python flow.py [--all | --extract | --upload | --analyze]")
        print("\nOptions:")
        print("  --all      Run all steps (extract → upload → analyze)")
        print("  --extract  Run only extract_store.py")
        print("  --upload   Run only upload.py")
        print("  --analyze  Run only analyze.py")
        sys.exit(1)
    
    option = sys.argv[1]
    
    if option == '--all':
        print("Running full pipeline...")
        run_script('video_data_extractor.py')
        run_script('extract_store.py')
        run_script('upload.py')
        run_script('analyze.py')
        print("\n" + "="*60)
        print("Full pipeline completed!")
        print("="*60)
        
    elif option == '--download':
        run_script('video_data_extractor.py')
    
    elif option == '--extract':
        run_script('extract_store.py')
        
    elif option == '--upload':
        run_script('upload.py')
        
    elif option == '--analyze':
        run_script('analyze.py')
  
    else:
        print(f"Unknown option: {option}")
        print("Use: --all, --extract, --upload, or --analyze")
        sys.exit(1)

if __name__ == "__main__":
    main()