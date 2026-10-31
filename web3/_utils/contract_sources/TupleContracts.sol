pragma solidity >=0.6.0;

contract TupleContract {
    struct T { int x; bool[2] y; address[] z; }
    struct S { uint a; uint[] b; T[] c; }

    event MethodCalled(S s);

    function method(S memory s) public pure returns (S memory) {
        return s;
    }
}

contract NestedTupleContract {
    struct U { int x; int y; }
    struct T { U[] u; }
    struct S { T[] t; }

    event MethodCalled(S s);

    function method(S memory s) public pure returns (S memory) {
        return s;
    }
}
