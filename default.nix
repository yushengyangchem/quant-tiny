{
  buildPythonPackage,
  hatchling,
  gitignoreSource,
  lib,
}:
let
  versionFile = builtins.readFile ./src/quant_tiny/__init__.py;
  versionLine = builtins.replaceStrings [ "\n" "\r" ] [ "" "" ] versionFile;
  versionMatch = builtins.match ''.*__version__ = "([^"]+)".*'' versionLine;
  version =
    if versionMatch == null then
      throw "Cannot find __version__ in src/quant_tiny/__init__.py"
    else
      builtins.head versionMatch;
in
buildPythonPackage {
  pname = "quant-tiny";
  inherit version;
  src = gitignoreSource ./.;
  pyproject = true;

  build-system = [ hatchling ];

  nativeBuildInputs = [ ];

  dependencies = [ ];

  doCheck = true;
  pythonImportsCheck = [ "quant_tiny" ];
  meta = {
    description = "A tiny & lightweight quantitative trading framework for learning";
    homepage = "https://github.com/yushengyangchem/quant-tiny";
    license = lib.licenses.mit;
    mainProgram = "quant-tiny";
    maintainers = [
      {
        name = "yushengyangchem";
        email = "yushengyangchem@gmail.com";
        github = "yushengyangchem";
      }
    ];
  };
}
