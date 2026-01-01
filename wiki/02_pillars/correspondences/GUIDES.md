# Guides to the Emerald Tablet

> *"Separate the earth from the fire, the subtile from the gross, acting prudently and with great judgment."*

These guides act as the manual for the **Correspondences Pillar**. Here you will learn to weave the Grid, summon formulas, and transmute data.

## How to Create a Table of Correspondences

1. **Open the Tablet**: Navigate to the Correspondences tool via the main menu or `Ctrl+3`.
2. **Define Your Headers**: Click on `A1`, `B1`, `C1` and type your headers (e.g., "Sephira", "God Name", "Number").
3. **Format the Headers**: Select the header row. Use the Toolbar to apply **Bold** (B) or a Background Color (Bucket Icon) to distinguish them.
4. **Enter Data**: Type your data into the rows below.

## How to Use Gematria Formulas

The Tablet's true power lies in its ability to calculate.

1. **Enter a Word**: In cell `A1`, type `Metatron`.
2. **Summon the Formula**: In cell `B1`, type `=GEMATRIA(A1, "Hebrew (Standard)")`.
3. **Behold the Result**: The cell will instantly display `314`.
4. **Drag to Fill**: If you have a list of names in A1:A10, select B1. precise click the small square in the bottom-right corner of the cell cursor (the Fill Handle) and drag it down to B10. The formula will automatically adjust (`=GEM(A2)`, `=GEM(A3)`, etc.).

## How to Import External Wisdom (CSV)

If you have existing tables (e.g., *Liber 777* data) in a CSV file:

1. Click the **Import CSV** folder icon in the toolbar.
2. Select your `.csv` file.
3. The Alchemist (Ingestion Service) will transmute the file into a new Scroll within your Tablet.

## How to Apply Conditional Formatting

To highlight values that meet certain criteria (e.g., all Names with value 93):

1. Select the range of numbers you wish to monitor.
2. Click the **Cond** button in the toolbar.
3. Choose **Equal To...** (or define a custom rule).
4. Enter `93` and select a color style.
5. Cells matching this value will now glow with the specified color.

## How to Export Your Work

*Note: Currently, only CSV export is supported. The Magus is working to bring JSON and Image export capabilities soon.*

1. Click the **Export CSV** floppy-disk icon.
2. Choose a destination.
3. Your active Scroll will be saved as a standard CSV file.
