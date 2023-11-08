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
    pyright.enable = true;
    ruff.enable = true;
    statix.enable = true;
    shellcheck.enable = true;
    taplo.enable = true;
    yamllint.enable = true;
  };

  processes = {
    serve.exec = "uvicorn tickflow.app.main:app --reload --host 127.0.0.1 --port 8000";
  };
}
