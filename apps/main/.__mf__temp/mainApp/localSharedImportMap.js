
// Windows temporarily needs this file, https://github.com/module-federation/vite/issues/68

    import {loadShare} from "@module-federation/runtime";
    const importMap = {
      
        "react": async () => {
          let pkg = await import("__mf__virtual/mainApp__prebuild__react__prebuild__.js");
            return pkg;
        }
      ,
        "react-dom": async () => {
          let pkg = await import("__mf__virtual/mainApp__prebuild__react_mf_2_dom__prebuild__.js");
            return pkg;
        }
      ,
        "vue": async () => {
          let pkg = await import("__mf__virtual/mainApp__prebuild__vue__prebuild__.js");
            return pkg;
        }
      
    }
      const usedShared = {
      
          "react": {
            name: "react",
            version: "19.2.3",
            scope: ["default"],
            loaded: false,
            from: "mainApp",
            async get () {
              if (false) {
                throw new Error(`Shared module '${"react"}' must be provided by host`);
              }
              usedShared["react"].loaded = true
              const {"react": pkgDynamicImport} = importMap
              const res = await pkgDynamicImport()
              const exportModule = {...res}
              // All npm packages pre-built by vite will be converted to esm
              Object.defineProperty(exportModule, "__esModule", {
                value: true,
                enumerable: false
              })
              return function () {
                return exportModule
              }
            },
            shareConfig: {
              singleton: true,
              requiredVersion: "^19.2.3",
              
            }
          }
        ,
          "react-dom": {
            name: "react-dom",
            version: "19.2.3",
            scope: ["default"],
            loaded: false,
            from: "mainApp",
            async get () {
              if (false) {
                throw new Error(`Shared module '${"react-dom"}' must be provided by host`);
              }
              usedShared["react-dom"].loaded = true
              const {"react-dom": pkgDynamicImport} = importMap
              const res = await pkgDynamicImport()
              const exportModule = {...res}
              // All npm packages pre-built by vite will be converted to esm
              Object.defineProperty(exportModule, "__esModule", {
                value: true,
                enumerable: false
              })
              return function () {
                return exportModule
              }
            },
            shareConfig: {
              singleton: true,
              requiredVersion: "^19.2.3",
              
            }
          }
        ,
          "vue": {
            name: "vue",
            version: "3.5.25",
            scope: ["default"],
            loaded: false,
            from: "mainApp",
            async get () {
              if (false) {
                throw new Error(`Shared module '${"vue"}' must be provided by host`);
              }
              usedShared["vue"].loaded = true
              const {"vue": pkgDynamicImport} = importMap
              const res = await pkgDynamicImport()
              const exportModule = {...res}
              // All npm packages pre-built by vite will be converted to esm
              Object.defineProperty(exportModule, "__esModule", {
                value: true,
                enumerable: false
              })
              return function () {
                return exportModule
              }
            },
            shareConfig: {
              singleton: true,
              requiredVersion: "^3.5.25",
              
            }
          }
        
    }
      const usedRemotes = [
      ]
      export {
        usedShared,
        usedRemotes
      }
      