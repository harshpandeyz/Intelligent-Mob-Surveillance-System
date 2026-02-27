// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EvidenceLog {
    struct Event {
        bytes32 hash;
        string metadata;
        uint256 timestamp;
        address reporter;
    }

    Event[] public events;

    event Logged(uint indexed id, bytes32 hash, string metadata, uint256 timestamp, address reporter);

    function logEvent(bytes32 _hash, string calldata _metadata) external {
        events.push(Event({
            hash: _hash,
            metadata: _metadata,
            timestamp: block.timestamp,
            reporter: msg.sender
        }));
        emit Logged(events.length - 1, _hash, _metadata, block.timestamp, msg.sender);
    }

    function getEvent(uint idx) external view returns (bytes32, string memory, uint256, address) {
        Event memory e = events[idx];
        return (e.hash, e.metadata, e.timestamp, e.reporter);
    }
}
