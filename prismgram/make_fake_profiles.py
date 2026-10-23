#!/usr/bin/env python3
"""
Re-issues Swiftgram's fake (self-signed) provisioning profiles for PrismGram's bundle id.

    python3 prismgram/make_fake_profiles.py /path/to/swiftgram-checkout com.prism.prismgram

The profiles in build-system/fake-codesigning/profiles are made for ph.telegra.Telegraph.
Telegram's build picks profiles by bundle id, so every occurrence of the old id is replaced
and the profile is signed again with build-system/fake-codesigning/certs/SelfSigned.p12.
Runs on macOS only (uses `security`).
"""

import datetime
import os
import plistlib
import re
import subprocess
import sys
import tempfile

OLD_BUNDLE_ID = "ph.telegra.Telegraph"


def p12_certificate_pem(p12):
    # OpenSSL 3 needs -legacy for this old p12, LibreSSL (macOS default) does not know the flag.
    for extra in (["-legacy"], []):
        result = subprocess.run(["openssl", "pkcs12", "-in", p12, "-passin", "pass:", "-nokeys"] + extra, capture_output=True)
        if b"BEGIN CERTIFICATE" in result.stdout:
            return result.stdout
    print("make_fake_profiles: could not read the certificate from " + p12)
    sys.exit(1)


def certificate_der(pem):
    return subprocess.run(["openssl", "x509", "-outform", "DER"], input=pem, check=True, capture_output=True).stdout


def certificate_common_name(pem):
    subject = subprocess.run(["openssl", "x509", "-noout", "-subject", "-nameopt", "oneline,-esc_msb"], input=pem, check=True, capture_output=True).stdout.decode("utf-8")
    match = re.search(r"CN\s*=\s*([^,/\n]+)", subject)
    if not match:
        print("make_fake_profiles: no CN in " + subject)
        sys.exit(1)
    return match.group(1).strip()


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    root = os.path.abspath(sys.argv[1])
    new_bundle_id = sys.argv[2]

    sys.path.insert(0, os.path.join(root, "build-system", "Make"))
    import GenerateProfiles  # noqa: E402  (Swiftgram's own helper)

    certs = os.path.join(root, "build-system", "fake-codesigning", "certs")
    profiles = os.path.join(root, "build-system", "fake-codesigning", "profiles")
    p12 = os.path.join(certs, "SelfSigned.p12")

    pem = p12_certificate_pem(p12)
    der = certificate_der(pem)
    identity = certificate_common_name(pem)
    print("signing identity: " + identity)

    keychain = GenerateProfiles.setup_temp_keychain(p12, "")
    try:
        count = 0
        for name in sorted(os.listdir(profiles)):
            if not name.endswith(".mobileprovision"):
                continue
            path = os.path.join(profiles, name)
            decoded = subprocess.run(["security", "cms", "-D", "-i", path], check=True, capture_output=True).stdout
            text = decoded.decode("utf-8").replace(OLD_BUNDLE_ID, new_bundle_id)
            profile = plistlib.loads(text.encode("utf-8"))
            profile["DeveloperCertificates"] = [der]
            profile.pop("DER-Encoded-Profile", None)
            # Swiftgram's fake profiles expire; keep ours valid so builds don't break on that date.
            now = datetime.datetime.utcnow().replace(microsecond=0)
            profile["CreationDate"] = now
            profile["ExpirationDate"] = now + datetime.timedelta(days=3650)
            profile["TimeToLive"] = 3650
            with tempfile.NamedTemporaryFile(suffix=".plist", delete=False) as tmp:
                tmp.write(plistlib.dumps(profile))
                plist_path = tmp.name
            subprocess.run(["security", "cms", "-S", "-k", keychain, "-N", identity, "-i", plist_path, "-o", path], check=True)
            os.unlink(plist_path)
            print("re-issued " + name + " -> " + profile["Entitlements"]["application-identifier"])
            count += 1
        if count == 0:
            print("make_fake_profiles: no profiles found")
            sys.exit(1)
    finally:
        GenerateProfiles.cleanup_temp_keychain(keychain)


if __name__ == "__main__":
    main()
