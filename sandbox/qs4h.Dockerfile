# The sandbox image for QS4h, QS4's code slice (Rounds/HonestHarness-R1/AMENDMENT-1.md, A1.4).
#
# P2's pinned base, the Docker Official Image python:3.12 on Debian trixie at its
# linux/amd64 digest (qs/agent/sandbox.py's IMAGE), with the project's dependencies
# installed when the image is built, since the sandbox has no network. The project
# imports httpx, jsonschema and pytest; their closure on Linux and CPython 3.12 is the
# 18 wheels below, each pinned by version and SHA-256 and installed with --no-deps.
# git is in the base image. Nothing else is added.
#
# Built by tools/qs4h_image.py, from an empty context:
#     docker build --network default -f sandbox/qs4h.Dockerfile <an empty directory>
# The build's container reaches PyPI (files.pythonhosted.org); every run's container is
# started with --network none. The requirements stay in the image, at
# /opt/qs4h/requirements.txt, so the image names its own pins.
FROM python:3.12-trixie@sha256:3d361d7fea344d55ac7a0f51ed7faa99213808ccc96fc9b9170adb95b6570b96

COPY <<EOF /opt/qs4h/requirements.txt
anyio==4.9.0 --hash=sha256:9f76d541cad6e36af7beb62e978876f3b41e3e04f2c1fbf0884604c0a9c4d93c
attrs==25.3.0 --hash=sha256:427318ce031701fea540783410126f03899a97ffc6f61596ad581ac2e40e3bc3
certifi==2025.4.26 --hash=sha256:30350364dfe371162649852c63336a15c70c6510c2ad5015b21c2345311805f3
h11==0.16.0 --hash=sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86
httpcore==1.0.9 --hash=sha256:2d400746a40668fc9dec9810239072b40b4484b640a8c38fd654a024c7a1bf55
httpx==0.28.1 --hash=sha256:d909fcccc110f8c7faf814ca82a9a4d816bc5a6dbfea25d6591d6985b8ba59ad
idna==3.7 --hash=sha256:82fee1fc78add43492d3a1898bfa6d8a904cc97d8427f683ed8e798d07761aa0
iniconfig==2.3.0 --hash=sha256:f631c04d2c48c52b84d0d0549c99ff3859c98df65b3101406327ecc7d53fbf12
jsonschema==4.23.0 --hash=sha256:fbadb6f8b144a8f8cf9f0b89ba94501d143e50411a1278633f56a7acf7fd5566
jsonschema-specifications==2024.10.1 --hash=sha256:a09a0680616357d9a0ecf05c12ad234479f549239d0f5b55f3deea67475da9bf
packaging==24.1 --hash=sha256:5b8f2217dbdbd2f7f384c41c628544e6d52f2d0f53c6d0c3ea61aa5d1d7ff124
pluggy==1.6.0 --hash=sha256:e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746
pygments==2.21.0 --hash=sha256:2363c69b61c4a97c838da3b130dcd6468f4848992b21a82f2a63ec34377137d9
pytest==9.1.1 --hash=sha256:37a86b45efb9a47a61a36449063e8e18d0cab3161329fc099eb21783169c4f0c
referencing==0.36.2 --hash=sha256:e8699adbbf8b5c7de96d8ffa0eb5c158b3beafce084968e2ea8bb08c6794dcd0
rpds-py==0.24.0 --hash=sha256:44d51febb7a114293ffd56c6cf4736cb31cd68c0fddd6aa303ed09ea5a48e029
sniffio==1.3.1 --hash=sha256:2f6da418d1f1e0fddd844478f41680e794e6051915791a034ff65e5f100525a2
typing-extensions==4.13.0 --hash=sha256:c8dd92cc0d6425a97c18fbb9d1954e5ff92c1ca881a309c45f06ebc0b79058e5
EOF

RUN PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_INPUT=1 PIP_ROOT_USER_ACTION=ignore \
    python3 -m pip install --no-cache-dir --no-deps --only-binary :all: --require-hashes \
        -r /opt/qs4h/requirements.txt \
 && PIP_DISABLE_PIP_VERSION_CHECK=1 python3 -m pip check
