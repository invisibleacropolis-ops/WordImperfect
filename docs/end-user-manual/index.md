# WordImperfect User Guide

Welcome! This manual keeps things simple so you can install WordImperfect, open your documents, and keep writing without getting stuck. Screenshots highlight the parts of the window you will click.

## Install WordImperfect

### Windows (64-bit)
1. Download the `WordImperfect-0.1.0-win-x64.exe` installer from the [Download page](../downloads/index.md).
2. Double-click the file. Windows may ask for confirmation because the installer came from the internet—choose **Run anyway**.
3. Follow the prompts. The default location installs WordImperfect in your user profile and adds a Start menu shortcut.
4. When setup finishes click **Launch WordImperfect**. A desktop shortcut is optional during installation.
5. (Recommended) Verify the installer checksum listed on the download page matches the SHA-256 value displayed in the wizard if your security policy requires it.

### macOS (Universal)
1. Download `WordImperfect-0.1.0-macos-universal.dmg`.
2. Double-click the `.dmg` file and drag **WordImperfect** into **Applications**.
3. Open Launchpad or Spotlight and run WordImperfect. If you see a gatekeeper warning, open **System Settings → Privacy & Security** and choose **Open Anyway** for WordImperfect.
4. Eject the mounted disk image after installation to tidy your Finder sidebar.

### Linux (x64)
1. Download `WordImperfect-0.1.0-linux-x64.AppImage`.
2. Mark the file as executable: `chmod +x WordImperfect-0.1.0-linux-x64.AppImage`.
3. Run the AppImage from a file manager or the terminal. Choose “Integrate and Run” if your desktop environment offers it.
4. Keep the AppImage somewhere stable or add it to your launcher manually. Update it when a new version appears on the download page.

> **Tip:** All installers live in `docs/downloads/artifacts/` inside this repository if you are working offline. The same folder lists SHA-256 checksums so you can verify every download.

## Everyday Tasks

### Open a document
![Screenshot: File → Open](images/open-document.png)

1. Choose **File → Open…**.
2. Pick your `.txt`, `.rtf`, or `.docx` file. These are the formats WordImperfect understands today.
3. The document loads into the main editing area. WordImperfect resets the formatting to the defaults if the file does not store extra styling.

### Save your work
![Screenshot: Save button and status highlight](images/save-document.png)

1. Click **File → Save** (or press `Ctrl+S` / `Cmd+S`).
2. The **Save As…** dialog appears the first time so you can choose a folder.
3. The status bar shows **Saved** when the file is written. Use **File → Save As…** to make a copy.

### Format text
![Screenshot: Formatting toolbar](images/formatting-toolbar.png)

1. Select the words you want to style.
2. Use the toolbar to change the **font**, **size**, **bold**, **italic**, or **underline**.
3. Alignment, lists, and indentation live in the same toolbar row—pick the button you need.
4. WordImperfect highlights the matching button when you move your cursor into formatted text.

### Find and replace text
![Screenshot: Find & Replace dialog highlight](images/find-replace.png)

1. Press `Ctrl+F` (`Cmd+F` on macOS) or choose **Edit → Find & Replace…**.
2. Type the word you are looking for and click **Find Next** to step through results.
3. Add replacement text and choose **Replace** or **Replace All** to update your document.
4. Use `F3` and `Shift+F3` to move forward or backward through the matches after the dialog opens.

## Troubleshooting

- **Fonts look wrong or too small.** Open the formatting toolbar and adjust the font family or size. WordImperfect remembers the new style for the selected text. If a font is missing entirely, install it in your operating system and restart the app.
- **“Unsupported file format” message.** WordImperfect currently works with `.txt`, `.rtf`, and `.docx`. Save the source file in one of those formats and try again.
- **Installer will not launch.** On Windows and macOS confirm the download is unblocked through SmartScreen or Gatekeeper. If the checksum differs from the value on the downloads page, redownload before running it again.
- **AppImage does nothing when I double-click it.** Make sure the file is executable (`chmod +x`) and that your desktop environment allows launching AppImages. Try running it from the terminal to read any error messages.

## Frequently Asked Questions

**Where does WordImperfect store my files?**  
Your documents stay wherever you save them. The Windows installer defaults to your Documents folder, but you can pick any location.

**Can I work with Microsoft Word files?**  
Yes. WordImperfect opens and saves `.docx` files through its document service. Complex layouts may simplify when you save them back, so keep a backup of heavily formatted documents.

**Does autosave exist?**  
Not yet. Use `Ctrl+S` (`Cmd+S`) regularly or keep the app open until you can save manually. Autosave is on the product roadmap.

**How do I update WordImperfect?**  
Open **Help → Check for Updates…** inside the app or revisit the [Download page](../downloads/index.md) to grab the latest installer.

**Who do I contact for help?**  
Email the support team at `support@wordimperfect.app` or open an issue on [GitHub](https://github.com/WordImperfect/WordImperfect/issues).

---

Need more detail? Advanced docs live alongside this guide in the `docs/` folder. Start with [`docs/writing-workflow.md`](../writing-workflow.md) for a deeper look at how the app manages formatting behind the scenes.
