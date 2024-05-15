#!/bin/bash

# default values
iterations=1
hostname=""
bandwidth="1M"
protocol="u"
bidir=""

# display help
show_help() {
    echo "Usage: $0 -i <iterations> -c <hostname> -b <bandwidth> -p <protocol> [--bidir]"
    echo "  -i      Number of iterations, 0 for infinite, 1 if not specified"
    echo "  -c      Hostname or IP address of remote iperf3 server"
    echo "  -b      Bandwidth for test, defaults to 1M if not specified"
    echo "  -p      Protocol of test, 'u' for udp or 't' for tcp, defaults to 'u'"
    echo "  --bidir Sets bidirectional mode if specified"
}

# clean up on exit
cleanup() {
    echo "... cleaning up and exiting..."
    exit 0
}

# trap ctrl+c
trap cleanup SIGINT

# parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -i) iterations="$2"; shift ;;
        -c) hostname="$2"; shift ;;
        -b) bandwidth="$2"; shift ;;
        -p) protocol="$2"; shift ;;
        --bidir) bidir="--bidir" ;;
        -h|--help) show_help; exit 0 ;;
        *) echo "Unknown parameter passed: $1"; show_help; exit 1 ;;
    esac
    shift
done

# validate inputs
if [[ -z "$hostname" ]]; then
    echo "Hostname or IP address is required."
    show_help
    exit 1
fi

if [[ "$protocol" != "u" && "$protocol" != "t" ]]; then
    echo "Invalid protocol. Use 'u' for UDP or 't' for TCP."
    show_help
    exit 1
fi

# convert protocol to iperf3 flag
if [[ "$protocol" == "u" ]]; then
    protocol_flag="-u"
else
    protocol_flag="-t"
fi

# main loop
i=0
while [[ "$iterations" -eq 0 || "$i" -lt "$iterations" ]]; do
    sleep 1
    iperf3 -c "$hostname" -b "$bandwidth" "$protocol_flag" "$bidir" -i 60 -t 60
    ((i++))
done
