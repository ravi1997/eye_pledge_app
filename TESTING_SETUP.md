#!/bin/bash

# Make run-tests.sh executable
chmod +x /home/programmer/Desktop/projects/aiims/eye_pledge_app/run-tests.sh

echo "✓ Test runner script is now executable"
echo ""
echo "To run the tests, use:"
echo ""
echo "  # Run all tests"
echo "  npm test"
echo ""
echo "  # Or use the convenient script:"
echo "  ./run-tests.sh"
echo ""
echo "  ./run-tests.sh headed        # See browser"
echo "  ./run-tests.sh debug         # Interactive debugging"
echo "  ./run-tests.sh pledge-form   # Test pledge form"
echo "  ./run-tests.sh ui-responsive # Test responsive design"
echo "  ./run-tests.sh report        # View test report"
