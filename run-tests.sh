#!/bin/bash

# Eye Donation Pledge System - Test Runner Script
# Quick commands for running Playwright tests

set -e

echo "================================"
echo "Eye Pledge App - Test Commands"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Get the command
COMMAND=${1:-help}

case $COMMAND in
    "run"|"test")
        echo -e "${BLUE}Running all tests...${NC}"
        npm test
        ;;
    
    "headed")
        echo -e "${BLUE}Running tests in headed mode (see browser)...${NC}"
        npm test -- --headed
        ;;
    
    "debug")
        echo -e "${BLUE}Running tests in debug mode (interactive)...${NC}"
        PWDEBUG=1 npm test
        ;;
    
    "report")
        echo -e "${BLUE}Showing test report...${NC}"
        npx playwright show-report
        ;;
    
    "trace")
        echo -e "${BLUE}Viewing trace files...${NC}"
        if [ -f "test-results/trace.zip" ]; then
            npx playwright show-trace test-results/trace.zip
        else
            echo -e "${YELLOW}No trace file found. Run tests first.${NC}"
        fi
        ;;
    
    "pledge-form")
        echo -e "${BLUE}Running pledge form tests...${NC}"
        npm test -- tests/pledge-form.spec.js
        ;;
    
    "ui-responsive")
        echo -e "${BLUE}Running UI/responsive tests...${NC}"
        npm test -- tests/ui-responsive.spec.js
        ;;
    
    "main")
        echo -e "${BLUE}Running main system tests...${NC}"
        npm test -- tests/pledge-system.spec.js
        ;;
    
    "chromium")
        echo -e "${BLUE}Running tests on Chromium browser...${NC}"
        npm test -- --project=chromium
        ;;
    
    "firefox")
        echo -e "${BLUE}Running tests on Firefox browser...${NC}"
        npm test -- --project=firefox
        ;;
    
    "webkit")
        echo -e "${BLUE}Running tests on WebKit browser...${NC}"
        npm test -- --project=webkit
        ;;
    
    "mobile")
        echo -e "${BLUE}Running tests on Mobile Chrome...${NC}"
        npm test -- --project="Mobile Chrome"
        ;;
    
    "watch")
        echo -e "${BLUE}Running tests in watch mode...${NC}"
        npm test -- --watch
        ;;
    
    "update")
        echo -e "${BLUE}Installing Playwright browsers...${NC}"
        npx playwright install
        ;;
    
    "help"|"-h"|"--help"|"")
        echo -e "${GREEN}Usage: ./run-tests.sh [command]${NC}"
        echo ""
        echo "Available commands:"
        echo ""
        echo "  Test Execution:"
        echo "    run              Run all tests (default)"
        echo "    headed           Run tests with visible browser"
        echo "    debug            Run tests in interactive debug mode"
        echo "    watch            Run tests in watch mode (rerun on changes)"
        echo ""
        echo "  Specific Test Suites:"
        echo "    pledge-form      Run pledge form workflow tests"
        echo "    ui-responsive    Run UI/responsive design tests"
        echo "    main             Run main system tests"
        echo ""
        echo "  Browser Selection:"
        echo "    chromium         Run on Chromium"
        echo "    firefox          Run on Firefox"
        echo "    webkit           Run on WebKit"
        echo "    mobile           Run on Mobile Chrome"
        echo ""
        echo "  Reporting:"
        echo "    report           View HTML test report"
        echo "    trace            View trace files from failed tests"
        echo ""
        echo "  Setup:"
        echo "    update           Install/update Playwright browsers"
        echo ""
        echo "Examples:"
        echo "  ./run-tests.sh headed          # See browser while running"
        echo "  ./run-tests.sh pledge-form     # Test form submission workflow"
        echo "  ./run-tests.sh chromium        # Test on Chrome only"
        echo "  ./run-tests.sh debug           # Interactive debugging"
        echo ""
        ;;
    
    *)
        echo -e "${YELLOW}Unknown command: $COMMAND${NC}"
        echo "Use './run-tests.sh help' for available commands"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Done!${NC}"
