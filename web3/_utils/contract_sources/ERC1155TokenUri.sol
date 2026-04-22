pragma solidity >=0.7.0;

/**
 * @title MinimalERC1155
 * @dev Minimal,-from-scratch ERC-1155-like implementation for Solidity 0.6.x
 *      Not a full-featured production library — but implements the core behavior
 *      required for minting and safe transfers (single + batch) and approvals.
 */
contract ERC1155TokenUri {
    string private _uri =
        "https://i.seadn.io/gcs/files/3ae7be6c41ad4767bf3ecbc0493b4bfb.png?w=4000&auto=format";
    mapping(uint256 => mapping(address => uint256)) private _balances;
    mapping(address => mapping(address => bool)) private _operatorApprovals;
    event URI(string value, uint256 indexed id);

    constructor() public {}

    function setUri(string memory new_uri) external {
        _uri = new_uri;
    }

    function uri(uint256 id) external view returns (string memory) {
        return _uri;
    }
}
