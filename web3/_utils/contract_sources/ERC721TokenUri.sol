// SPDX-License-Identifier: MIT
pragma solidity >=0.7.0 <0.9.0;

/**
 * @title ERC721
 * @dev Minimal ERC-721 stub that only exposes `tokenURI(uint256)`
 *      Used for metadata or ENS avatar resolution tests.
 */
contract ERC721TokenUri {
    // Static URI — same for all token IDs
    string private _uri =
        "https://i.seadn.io/gcs/files/3ae7be6c41ad4767bf3ecbc0493b4bfb.png?w=4000&auto=format";

    constructor() {}

    function setUri(string memory new_uri) external {
        _uri = new_uri;
    }

    /**
     * @notice Returns the same metadata URI for any tokenId.
     */
    function tokenURI(
        uint256 /* tokenId */
    ) external view returns (string memory) {
        return _uri;
    }
}
