#!/bin/bash

# Svalbard Species Map - Map Generation Only Script
# This script runs only the species distribution map generation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if data exists
check_data() {
    if [ ! -f "data/all_species_occurrences.csv" ]; then
        print_error "No occurrence data found!"
        print_status "Please run the download pipeline first:"
        print_status "  ./run_docker.sh run"
        print_status "  or"
        print_status "  python download_gbif_data.py"
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "Svalbard Species Map - Map Generation Only"
    echo "=========================================="
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  generate  Generate species distribution maps"
    echo "  test      Test map generation with sample data"
    echo "  help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 generate"
    echo "  $0 test"
    echo
    echo "Requirements:"
    echo "  - Occurrence data in data/all_species_occurrences.csv"
    echo "  - Python dependencies installed"
    echo
    echo "Output:"
    echo "  data/maps/  Directory containing generated maps"
}

# Function to generate maps
generate_maps() {
    print_status "Generating species distribution maps..."
    print_status "This will create maps for each species and a combined view."
    echo
    
    if command -v python3 &> /dev/null; then
        python3 generate_species_maps.py
    elif command -v python &> /dev/null; then
        python generate_species_maps.py
    else
        print_error "Python not found. Please install Python to use this feature."
        exit 1
    fi
    
    print_success "Map generation completed!"
    print_status "Maps saved in: data/maps/"
}

# Function to run map tests
run_map_tests() {
    print_status "Running map generation tests..."
    print_status "This will create sample data and test map generation."
    echo
    
    if command -v python3 &> /dev/null; then
        python3 test_maps.py
    elif command -v python &> /dev/null; then
        python test_maps.py
    else
        print_error "Python not found. Please install Python to use this feature."
        exit 1
    fi
    
    print_success "Map tests completed!"
}

# Main script logic
main() {
    # Parse command
    case "${1:-help}" in
        generate)
            check_data
            generate_maps
            ;;
        test)
            run_map_tests
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@" 