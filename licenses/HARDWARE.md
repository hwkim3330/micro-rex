# Hardware, geometry and attribution

Original Microduck model and meshes: **Pollen Robotics**.
Source: https://github.com/pollen-robotics/microduck_rl
The exact source commit is recorded in `upstream.lock.json`.

The upstream README states: “Hardware design files are licensed under Creative Commons BY-SA-NC.”
It does not specify a version in that notice. The unmodified model files and STL meshes in
`vendor/microduck/` retain those upstream terms; this repository does not relicense them as Apache.
`vendor/microduck/UPSTREAM_README.md` preserves the original notice.

New Micro Rex CAD geometry, derivative assembly meshes, model XML, drawings and renderings:
Copyright 2026 hwkim3330, **CC BY-NC-SA 4.0**, subject also to the original upstream hardware terms.
Attribution: “Micro Rex by hwkim3330, based on Microduck by Pollen Robotics.”
Changes: T-rex cheek shells, decorative teeth/brows, bridges, forelimbs, brackets and tail;
additive inertial properties; assembled reference models and derived drawings.
Non-commercial use only; preserve attribution and ShareAlike when redistributing derivatives.

New build/validation/viewer software is Apache-2.0, except Three.js vendored files,
which retain their included MIT license in `web/vendor/three/LICENSE`.

The community `microduck-replica` and official electronics repositories are linked/pinned as
upstream submodules; their respective licenses remain authoritative. Community reconstructions
are not factory drawings, and are not described as physically verified Micro Rex hardware.

License text for new Micro Rex design work:
https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en
