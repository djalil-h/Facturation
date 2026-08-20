# Hamzaoui Facturation — build Windows

## Principe

L'installateur produit `Hamzaoui-Facturation-Setup-v2.0.exe`.

Le programme est installé dans `Program Files`, tandis que les données de production restent dans :

`%LOCALAPPDATA%\Hamzaoui Facturation\`

La base de production est donc :

`%LOCALAPPDATA%\Hamzaoui Facturation\database\facturation.db`

Les sauvegardes sont dans :

`%LOCALAPPDATA%\Hamzaoui Facturation\backups\`

Une mise à jour de l'application ne remplace pas la base existante.

## Build automatique recommandé

Le workflow GitHub Actions `.github/workflows/build-windows-installer.yml` peut être lancé manuellement avec **Run workflow**.

Il :

1. installe Python 3.12 et les dépendances ;
2. génère l'icône Windows depuis `assets/hamzaoui_logo.svg` ;
3. construit `HamzaouiFacturation.exe` avec PyInstaller ;
4. construit le Setup avec Inno Setup ;
5. publie le Setup comme artifact GitHub Actions.

## Build local

Sur Windows avec Python 3.12 :

```powershell
python -m pip install -r requirements.txt
python -m pip install pyinstaller pillow cairosvg
python -c "import cairosvg; cairosvg.svg2png(url='assets/hamzaoui_logo.svg', write_to='assets/hamzaoui_logo.png', output_width=512, output_height=512)"
python -c "from PIL import Image; im=Image.open('assets/hamzaoui_logo.png').convert('RGBA'); im.save('assets/hamzaoui_logo.ico', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"
pyinstaller --noconfirm --clean --windowed --onedir --name HamzaouiFacturation --icon assets/hamzaoui_logo.ico --add-data "assets;assets" main.py
```

Puis compiler `installer/HamzaouiFacturation.iss` avec Inno Setup 6.

## Important

Ne jamais inclure `database/facturation.db` dans le Setup. La base de production appartient aux données utilisateur et doit être conservée lors des mises à jour.
