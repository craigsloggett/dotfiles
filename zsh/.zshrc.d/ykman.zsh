yubikey-signing-key() {
  local serial
  serial="$(ykman list --serials 2>/dev/null | head -n 1)"

  [ -n "${serial}" ] || {
    print -u2 'No YubiKey attached.'; return 1
  }

  git config --file "${XDG_CONFIG_HOME}/git/config-personal" user.signingKey "${HOME}/.ssh/id_ed25519_sk_rk_${serial}"
}
