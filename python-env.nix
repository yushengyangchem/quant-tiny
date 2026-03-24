{
  pkgs,
  pythonVersion,
  gitignoreSource,
}:
let
  pythonEnv = pkgs.${pythonVersion}.override {
    packageOverrides = self: super: {
      quant_tiny = self.callPackage ./. { inherit gitignoreSource; };
    };
  };
in
pythonEnv
