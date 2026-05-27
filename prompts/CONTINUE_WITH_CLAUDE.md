# Continue With Claude

Use this prompt to hand the project to Claude or another coding agent.

```text
Tu reprends un portage Unreal Engine vers le fork VITE/UE4.27.

Langue de travail: francais.
Shell: PowerShell sur Windows.
Repo de documentation:
D:\PORTAGE_VITE\ue5-downgrader

Projet source UE5.7 Downgrader:
D:\PORTAGE_VITE\CounterStrike_5_7_DowngradeSource\CounterStrike.uproject

Moteur source custom Asset Downgrader:
C:\Users\Capet9800X3D\Desktop\UNREAL ASSET DOWNGRADER (5.7)\UE_5.7.4_Downgrader\Engine\Binaries\Win64\UnrealEditor.exe

Projet cible VITE stable:
D:\PORTAGE_VITE\CounterStrike_VITE_From57_CoreOnly_NoDowngrader\CounterStrike_VITE_From57_CoreOnly_NoDowngrader.uproject

Moteur VITE:
D:\CLONE VITE UE5\Engine\Binaries\Win64\UE4Editor.exe

Contexte important:
- Le portage precedent de la map est rejete.
- /Game/Maps/MAP_Main_VITE_Auto charge et resave dans VITE mais ne correspond pas visuellement a la map source.
- /Game/Maps/MAP_Main_VisualOnly a ete supprime apres verification visuelle ratee.
- Ne pas repartir de MAP_Main_VITE_Auto comme map valide.
- Ne pas copier directement Content/Maps/MAP_Main.umap dans VITE: le package source/downgrade precedent est incompatible ou visuellement faux.

Lire d'abord:
D:\PORTAGE_VITE\ue5-downgrader\README.md
D:\PORTAGE_VITE\ue5-downgrader\docs\ASSET_DOWNGRADER_NOTES.md
D:\PORTAGE_VITE\ue5-downgrader\docs\PASS_0_RESTART_PLAN.md
D:\PORTAGE_VITE\ue5-downgrader\docs\PASS_0_RESULTS.md
D:\PORTAGE_VITE\ue5-downgrader\docs\MAP_RECONSTRUCTION.md
D:\PORTAGE_VITE\ue5-downgrader\docs\PORTAGE_STATUS.md
D:\PORTAGE_VITE\ue5-downgrader\docs\REMAINING_WORK.md
D:\PORTAGE_VITE\ue5-downgrader\docs\CRASHES_AND_FIXES.md

Etat Pass 0 deja fait:
- Export source v2 genere depuis la vraie map UE5.7:
  D:\PORTAGE_VITE\Pass0_SourceReference\MAP_Main_SourceVisual_v2.json
  D:\PORTAGE_VITE\Pass0_SourceReference\MAP_Main_SourceVisual_v2_Summary.json
- Script reproductible:
  D:\PORTAGE_VITE\Scripts\pass0_export_visual_v2_ue57.py
  repo copy: D:\PORTAGE_VITE\ue5-downgrader\scripts\pass0_export_visual_v2_ue57.py
- Export counts:
  Actors: 462
  Scene components: 766
  Static mesh components: 364
  Light components: 4
  Audio components: 1
  Script export errors: 0
- Le commandlet UE5.7 sort avec code 1 a cause des erreurs Blueprint/Animation/ControlRig connues au chargement, mais l'export Python est complet.

Travail immediat:
1. Ouvrir la vraie map source UE5.7:
   /Game/Maps/MAP_Main
2. Capturer des screenshots de reference depuis le viewport UE5.7:
   - perspective overview
   - top orthographic
   - side/front orthographic si possible
3. Construire une nouvelle map cible VITE:
   /Game/Maps/MAP_Main_VisualOnly_V2
4. Utiliser l'export v2, pas l'ancien JSON v1.
5. Pour les meshes, reconstruire depuis les transforms de composants, pas depuis un actor transform simplifie.
6. Comparer source vs cible:
   - counts par classe
   - counts par mesh path
   - transforms
   - bounds
   - materials
   - screenshots
7. Seulement apres validation visuelle, reprendre gameplay/spawns/armes/widgets.

Contraintes:
- Ne pas reactiver le plugin Downgrader dans le projet VITE runtime/validation.
- Ne pas supprimer les quarantines.
- Ne pas remettre Content/Dependencies dans Content actif sans validation isolee.
- Ne pas utiliser les widgets incompatibles directement:
  /Game/UI/WB_Crosshair
  /Game/UI/WB_Main
  /Game/UI/WB_TeamSelection
- Les Blueprints gameplay originaux sont instables dans VITE:
  BP_AK47, BP_M4A1, BP_Pistol, BP_TerroristSpawnPoint, BP_CounterTerroristSpawnPoint.
- Si tu modifies des assets Unreal, lis/dump avant mutation, puis verifie apres mutation.
- Si tu ecris du C++ Unreal, verifie les signatures avec Unreal API docs/MCP avant de coder.

Liens Asset Downgrader:
- Fab: https://www.fab.com/listings/86a0ce48-ff38-493c-906d-8d2297067ee6
- Tutorial/demo: https://www.youtube.com/watch?v=yXvJfDNfrSQ
- Custom engine/plugin downloads: https://drive.google.com/drive/folders/1jvPfzknzWHo_diP3k9OJhAmRQZQSjQ7v

Quand une etape est terminee, mets a jour le repo docs et commit/push sur:
https://github.com/Capetlevrai/ue5-downgrader
```

## MCP To Install Or Enable

Minimum useful MCP/tooling for Claude:

1. **Unreal Engine MCP bridge**
   - Needed to inspect editor state, load levels, read actors/assets, run editor Python, capture screenshots, and validate maps.
   - Required capabilities:
     - `project.get_status`
     - `editor.execute_python` or `editor.run_python_file`
     - `editor.capture_screenshot` or `editor.capture_scene_png`
     - `editor.get_viewport` / `editor.set_viewport`
     - `level.get_outliner`
     - `asset.search/read/read_properties`
     - `reflection.reflect_class`
   - In this Codex session, the equivalent servers were:
     - `ue-mcp-counterstrike`
     - `ue-mcp-fps-cs-5-4`

2. **Unreal API reference MCP**
   - Needed before writing Unreal C++ or unfamiliar Python/editor API usage.
   - In this Codex session, equivalent tools were exposed as:
     - `unreal-api`
     - `unreal-api-counterstrike`

3. **Filesystem + PowerShell access**
   - Required for scripts, logs, git, and commandlets.
   - The project is Windows/PowerShell based.

4. **Optional: lean-ctx**
   - Useful for compact reads/searches in large trees.
   - Not strictly required if Claude already has good file search/read tools.

5. **Optional: Browser MCP**
   - Only needed if Claude must inspect Fab/YouTube/docs in-browser.
   - Not required for the immediate Pass 0/Pass 1 work.

## First Commands To Verify Environment

```powershell
git -C D:\PORTAGE_VITE\ue5-downgrader status --short

Test-Path 'C:\Users\Capet9800X3D\Desktop\UNREAL ASSET DOWNGRADER (5.7)\UE_5.7.4_Downgrader\Engine\Binaries\Win64\UnrealEditor.exe'
Test-Path 'D:\CLONE VITE UE5\Engine\Binaries\Win64\UE4Editor.exe'
Test-Path 'D:\PORTAGE_VITE\Pass0_SourceReference\MAP_Main_SourceVisual_v2.json'
```

## Known Launch Note

Codex tried to start the visible UE5.7 editor with `Start-Process`, but Windows returned:

```text
L'operation a ete annulee par l'utilisateur.
```

If that happens again, launch manually:

```text
D:\PORTAGE_VITE\Start_CounterStrike_5_7_DowngradeSource.bat
```

Then open:

```text
/Game/Maps/MAP_Main
```
