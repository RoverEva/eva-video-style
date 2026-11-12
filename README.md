Verified `EVA-Core.zip` 1.0.1 (sha256 5c8bd576edd85b49d074feae9c82cb5b1669ba895d629075363977d210b7be53), built deterministically
from `codex/v1.0-source-only-rc` @ 4e7a4db with the same toolchain as the v1.0.0 assets (zlib-ng deflate). Stock zlib on
GitHub runners produces different compressed bytes for identical contents, so the publish workflow uploads THIS file after
checking that its sha256 matches the committed SHA256SUMS and that every member is byte-identical to the release source.
