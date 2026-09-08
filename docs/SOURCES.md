# Sources and scope

Four public repositories were cloned for this work. Exact commits are pinned in `upstream.lock.json` and `.gitmodules` / gitlinks.

| Source | Role | What is and is not established |
|---|---|---|
| [pollen-robotics/microduck](https://github.com/pollen-robotics/microduck) | Official Rust control runtime | Runtime source, configuration and control contract; not a Micro Rex firmware validation |
| [pollen-robotics/microduck_rl](https://github.com/pollen-robotics/microduck_rl) | Official training source, MJCF and STL | Actual reference model used here. `robot_walk.xml` has 14 policy actuators; the runtime's mouth channel is separate |
| [pollen-robotics/elec_RPI_Robot_HAT](https://github.com/pollen-robotics/elec_RPI_Robot_HAT) | Official KiCad electronics | Includes schematic, PCB, production outputs and BOM. Presence of this board does not establish a complete factory robot build package |
| [fanhao375/microduck-replica](https://github.com/fanhao375/microduck-replica) | Community reconstruction | Assembly drawings, inferred mechanical/electronic details; treated as third-party reconstruction, not authoritative factory drawings |

The upstream MJCF links an Onshape document. We preserve the link inside the original XML but do not claim to have retrieved editable original Onshape parts.

The new CAD generator, drawings, build files and viewer are original work in this repository. The complete robot render/GLB and MuJoCo derivative use the official Microduck meshes and preserve their attribution and hardware licensing. No community CAD is silently represented as an original manufacturer file.

`vendor/microduck/` is a ready-to-use snapshot of the official model files and meshes. Full upstream software and hardware repositories are pinned submodules under `upstream/`; retrieve them using `git clone --recurse-submodules`.

The static renders show the reference assembly pose. They are computer-generated views of the delivered model, not photographs of a built Micro Rex.

## Interactive design references

The following user-supplied Spaces were inspected as interaction references. Their application code and additional assets were not copied into this site:

- [Microduck simulator](https://huggingface.co/spaces/pollen-robotics/microduck-simulator), revision `e81974b932c7ca1819843b7bb3dcd42e2993e98e`: simulator presentation and controls.
- [Microduck anatomy](https://huggingface.co/spaces/mishig/microduck-anatomy), revision `5329ff5db7c6baa5c15def88085f842e0221395e`: inspectable anatomy and articulated model interaction.
- [Reachy Mini 3D voice](https://huggingface.co/spaces/pollen-robotics/reachy-mini-3d-voice), revision `bdcac3f73e9b7def1a71ee03d2ca7a858fd0004b`: character and robot presentation.

Our browser rig is independently exported from the vendored upstream MJCF using `tools/export_rig.py`. It preserves body hierarchy, local joint axes, pivots and ranges. It is a kinematic viewer, without collision enforcement, balance control or a voice backend. Moving a slider is not evidence of feasible hardware motion.
