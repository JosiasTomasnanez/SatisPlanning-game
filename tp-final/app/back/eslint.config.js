// Configuración de ESLint (formato "flat", ESLint 9) SIN dependencias externas:
// no importa @eslint/js ni plugins, así el CI no necesita npm install para
// lintear. Las reglas se eligen a mano: las que detectan errores reales o
// malas prácticas que afectan la mantenibilidad y la seguridad del back.
module.exports = [
  {
    files: ['**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'commonjs',
      // Globales de Node.js declaradas a mano (sin el paquete "globals").
      globals: {
        require: 'readonly',
        module: 'writable',
        process: 'readonly',
        console: 'readonly',
        Buffer: 'readonly',
        setTimeout: 'readonly',
        clearTimeout: 'readonly',
        __dirname: 'readonly',
      },
    },
    rules: {
      // Errores reales
      'no-undef': 'error',              // variable no declarada (typo)
      'no-unused-vars': 'error',        // código muerto
      'no-unreachable': 'error',        // código después de un return
      'no-dupe-keys': 'error',
      'no-empty': 'error',              // catch vacío que esconde errores
      'consistent-return': 'error',     // handlers que a veces responden y a veces no
      // Seguridad
      'no-eval': 'error',
      'no-implied-eval': 'error',
      'no-new-func': 'error',
      // Mantenibilidad
      eqeqeq: 'error',                  // == hace conversiones implícitas
      'no-var': 'error',
      'prefer-const': 'error',
    },
  },
];
