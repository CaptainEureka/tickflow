{pkgs, ...}: {
  packages = [pkgs.git];

  languages = {
    nix.enable = true;
    python = {
      enable = true;
      version = "3.12";
      poetry = {
        enable = true;
        activate.enable = true;
      };
    };
  };

  pre-commit.hooks = {
    alejandra.enable = true;
    ruff.enable = true;
    statix.enable = true;
    shellcheck.enable = true;
    taplo.enable = true;
    yamllint.enable = true;
  };
}
