#!/bin/bash

# Svalbard Species Map - Docker Runner Script
# This script helps run the GBIF data download pipeline with Docker

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to check credentials
check_credentials() {
    if [ ! -f ".env" ] && [ -z "$GBIF_USERNAME" ] && [ -z "$GBIF_PASSWORD" ]; then
        print_warning "No GBIF credentials found!"
        print_status "You need GBIF credentials to get a DOI for your dataset."
        print_status "You can:"
        print_status "1. Run: python setup_credentials.py"
        print_status "2. Create a .env file with GBIF_USERNAME and GBIF_PASSWORD"
        print_status "3. Set environment variables"
        print_status "4. Update gbif_config.py"
        echo
        read -p "Continue without credentials? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Please set up credentials first."
            exit 1
        fi
    fi
}

# Function to show help
show_help() {
    echo "Svalbard Species Map - Docker Runner"
    echo "===================================="
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  build     Build the Docker image"
    echo "  run       Run the complete download pipeline"
    echo "  test      Run tests only"
    echo "  logs      Show container logs"
    echo "  clean     Remove containers and images"
    echo "  setup     Set up GBIF credentials"
    echo "  help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 run"
    echo "  $0 test"
    echo
    echo "Environment Variables:"
    echo "  GBIF_USERNAME    Your GBIF email address"
    echo "  GBIF_PASSWORD    Your GBIF password"
    echo
    echo "Files:"
    echo "  .env             Credentials file (auto-created by setup)"
    echo "  data/            Downloaded data directory"
    echo "  logs/            Log files directory"
}

# Function to build Docker image
build_image() {
    print_status "Building Docker image..."
    docker-compose build
    print_success "Docker image built successfully!"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    docker-compose run --rm gbif-downloader python test_download.py
    print_success "Tests completed!"
}

# Function to run full pipeline
run_pipeline() {
    print_status "Running GBIF download pipeline..."
    print_status "This will download data for all species and generate a DOI."
    print_status "The process may take up to 1 hour for large datasets."
    echo
    
    docker-compose up --build
    print_success "Pipeline completed!"
}

# Function to show logs
show_logs() {
    print_status "Showing container logs..."
    docker-compose logs -f
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    docker-compose down --rmi all --volumes --remove-orphans
    print_success "Cleanup completed!"
}

# Function to setup credentials
setup_credentials() {
    print_status "Setting up GBIF credentials..."
    if command -v python3 &> /dev/null; then
        python3 setup_credentials.py
    elif command -v python &> /dev/null; then
        python setup_credentials.py
    else
        print_error "Python not found. Please install Python to use this feature."
        exit 1
    fi
}

# Main script logic
main() {
    # Check if Docker is available
    check_docker
    
    # Parse command
    case "${1:-help}" in
        build)
            build_image
            ;;
        run)
            check_credentials
            run_pipeline
            ;;
        test)
            run_tests
            ;;
        logs)
            show_logs
            ;;
        clean)
            cleanup
            ;;
        setup)
            setup_credentials
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