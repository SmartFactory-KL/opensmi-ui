const vibrantColors = [
  "Crimson",
  "RoyalBlue",
  "DarkOrange",
  "MediumVioletRed",
  "Tomato",
  "DodgerBlue",
  "FireBrick",
  "BlueViolet",
  "DarkRed",
  "Teal",
  "DeepPink",
  "Indigo",
  "HotPink",
  "SeaGreen",
  "Purple",
  "ForestGreen",
  "OrangeRed",
  "MediumBlue",
  "DarkViolet",
  "DarkGreen",
] as const;


class ColorPick {
  getRandomColor() {
    return vibrantColors[Math.floor(Math.random() * vibrantColors.length)];
  }
  getIndexedColor(idx: number = 0) {
    return vibrantColors[idx % vibrantColors.length];
  }
}

export default new ColorPick();
