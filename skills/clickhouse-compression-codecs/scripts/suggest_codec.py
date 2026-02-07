import argparse
import sys

def get_codec(data_type, is_monotonic):
    """
    Returns the optimal ClickHouse CODEC string based on type and pattern.
    """
    dt = data_type.lower()
    
    # --- 1. Special Handling for Monotonic Data (Sequences) ---
    # Best for: Timestamps, Auto-increment IDs
    if is_monotonic:
        # DoubleDelta is best for constant strides (e.g., exactly 1s intervals or ID+1)
        if any(x in dt for x in ['date', 'time', 'int']):
            return "CODEC(DoubleDelta, ZSTD(1))"
        # Gorilla is best for monotonic floats (rare, but possible)
        if 'float' in dt:
             return "CODEC(Gorilla, ZSTD(1))"

    # --- 2. Time/Date (General / Random order) ---
    # Delta is good for reducing the magnitude of values relative to each other
    if any(x in dt for x in ['date', 'time']):
        return "CODEC(Delta, ZSTD(1))"

    # --- 3. Floats (General) ---
    # Gorilla is specialized for floating point bit patterns
    if 'float' in dt:
        return "CODEC(Gorilla, ZSTD(1))"

    # --- 4. Integers (General / Random) ---
    # T64 is an option, but ZSTD is generally safer and more balanced.
    if 'int' in dt:
        return "CODEC(ZSTD(1))"

    # --- 5. Strings / FixedStrings ---
    # LowCardinality is a data type, not a codec, but if the underlying type is String:
    if 'string' in dt:
        return "CODEC(ZSTD(1))"
    
    # --- 6. Fallback ---
    return "CODEC(ZSTD(1))"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Suggest ClickHouse Codec")
    parser.add_argument("--data_type", required=True, help="The ClickHouse data type (e.g., DateTime, String)")
    parser.add_argument("--is_monotonic", type=str, default="false", help="Is the data strictly increasing? (true/false)")
    
    args = parser.parse_args()
    
    # Convert string argument to boolean safely
    is_monotonic_bool = args.is_monotonic.lower() in ('true', '1', 'yes')
    
    suggestion = get_codec(args.data_type, is_monotonic_bool)
    
    # Output solely the codec string for the agent to consume
    print(suggestion)
