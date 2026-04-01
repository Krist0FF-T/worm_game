{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python313
    pkgs.python313Packages.pygame-ce
  ];

  shellHook = ''
    echo "Simply run 'python3 main.py' to run the simulator!"
  '';
}
