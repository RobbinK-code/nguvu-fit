import { useTheme } from "./ThemeContext";

const PALETTES = {
  light: { grid: "#ece5d8", axisText: "#736c60", accent: "#ff5a36", success: "#2fb673" },
  dark: { grid: "#2c3638", axisText: "#9a978f", accent: "#ff6b45", success: "#45c98a" },
};

export function useChartColors() {
  const { theme } = useTheme();
  return PALETTES[theme] || PALETTES.light;
}
