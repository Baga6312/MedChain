import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const dark = theme === 'dark';
  return (
    <button className="theme-toggle" type="button" onClick={toggleTheme} aria-label={dark ? 'Activer le mode clair' : 'Activer le mode sombre'} title={dark ? 'Mode clair' : 'Mode nuit'}>
      {dark ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  );
}
