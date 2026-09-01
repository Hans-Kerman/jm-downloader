{
  description = "jm-api downloader Python environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      py = pkgs.python312Packages;

      # jmcomic 依赖链中仅有的两个 nixpkgs 缺失包，用 PyPI wheel 内联打包
      commonx = py.buildPythonPackage rec {
        pname = "commonx";
        version = "0.6.39";
        format = "wheel";
        src = py.fetchPypi {
          inherit pname version;
          format = "wheel";
          dist = "py3";
          python = "py3";
          hash = "sha256-QC1UeXQz8xmEpf9DmBrkUd5hY0bY/pLiV24/lzACUgI=";
        };
        propagatedBuildInputs = [ ];
        doCheck = false;
      };

      jmcomic = py.buildPythonPackage rec {
        pname = "jmcomic";
        version = "2.6.10";
        format = "wheel";
        src = py.fetchPypi {
          inherit pname version;
          format = "wheel";
          dist = "py3";
          python = "py3";
          hash = "sha256-zdO4X3R+/OjYczNPeqnytF5TcQJ4EdNkLJsWwfgh5TM=";
        };
        propagatedBuildInputs = with py; [
          commonx
          curl-cffi
          pillow
          pycryptodome
          pyyaml
        ];
        doCheck = false;
      };

      pythonEnv = pkgs.python312.withPackages (ps: [
        jmcomic
        ps.openai
        ps.python-dotenv
        ps.pip
      ]);
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ pythonEnv ];
      };
    };
}
