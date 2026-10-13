# NFS III Reversed Engineered

Reverse engineering and decompilation of **Need for Speed III: Hot Pursuit** using Ghidra. The completed static analysis pass includes descriptive function names, comments, types, and references. Complex follow-up investigations are documented separately; this project provides an annotated Ghidra database rather than a buildable game reconstruction.

The target is based on [VEG's Modern Patch v1.6.1](https://veg.by/en/projects/nfs3/), with small copyright and version-text changes in `nfs3.exe` and the setup menu preparing our local **1.6.2** version. See [target provenance](docs/TARGET.md) for details and the executable fingerprint.

![NFS III analysis in Ghidra](images/nfs3_ghidra.png)

*The annotated Ghidra project includes descriptive function names, comments, types, and references. 99.4% of internal functions have names.*

## Install Ghidra

1. Download the latest stable release from [Ghidra releases](https://github.com/NationalSecurityAgency/ghidra/releases). Under **Assets**, choose the **`.zip` with `PUBLIC` in its name**, such as `ghidra_<version>_PUBLIC_<date>.zip`. Avoid the **Source code** archives.
2. Install the **64-bit JDK** required by that release, as documented in its bundled `GettingStarted.html`. Our current environment uses **Ghidra 12.1.4 and JDK 21**. The JDK includes the Java runtime; a standalone JRE is insufficient.
3. Extract Ghidra into a new directory and launch `./ghidraRun` on Linux/macOS or `ghidraRun.bat` on Windows.

On Debian, Ubuntu, Linux Mint, and derivatives where the default JDK provides Java 21:

```sh
sudo apt update
sudo apt install default-jdk
```

Check with `java -version` and `javac -version`. Older distribution releases may default to an older JDK. If needed, install [Temurin 21](https://adoptium.net/temurin/releases/?version=21) separately. If Ghidra asks for a Java location, select the JDK directory containing `bin/`.

## Clone and open

```sh
git clone https://github.com/melroy89/nfs3-re.git
cd nfs3-re
```

The checkout includes the complete Ghidra project layout:

```text
nfs3-re/
├── README.md
├── nfs3_decomp.gpr
└── nfs3_decomp.rep/
    ├── project.prp
    ├── idata/
    └── versioned/
```

The `.gpr` file is an empty project marker; the analysis is stored in the matching `.rep` directory. Keep them together.

1. In Ghidra, choose **File → Open Project** and select **`nfs3-re/nfs3_decomp.gpr`**.
2. Expand **Electronic Arts → Need For Speed III** and double-click **nfs3.exe**.
3. Select a function under **Symbol Tree → Functions** to inspect its assembly and pseudocode. Use **Window → Decompiler** if the pane is hidden, or press **G** to navigate to an address.

The standalone `nfs3_decomp.rep/Electronic Arts/` game directory is excluded and is **not needed to browse the saved analysis**. The similarly named folder inside Ghidra is part of the database. Game files are needed separately to run the game.

Save regularly. Save and close Ghidra before committing database changes, making backups, or upgrading. See [release preparation](docs/RELEASE.md) for validation status.

## Contributing and license

See [contribution guidance](CONTRIBUTING.md), [sharing analysis](docs/SHARING.md), and [release preparation](docs/RELEASE.md).

Original contributions are licensed under **Apache-2.0**; see [LICENSE](LICENSE) and [NOTICE](NOTICE). This does not relicense the game, VEG's patch, or imported third-party bytes in the databases. Review redistribution rights before publication.

Credit to Electronic Arts, VEG, and the Ghidra authors. This independent project claims no affiliation or endorsement.
