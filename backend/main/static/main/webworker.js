importScripts("../../pyodide/pyodide.js");

onmessage = async function (e) {
  try {
    const data = e.data;
    let result;
    switch (data.type) {
      case 'loadPyodide':
        self.pyodide = await loadPyodide();
        self.pyodide.loadPackage("jinja2")
        result = JSON.stringify({ pyodideLoaded: true });
        break;
      case 'python':
        self.pythonContext = data.pythonContext || {};
        result = await self.pyodide.runPythonAsync(data.python) || "{}";
        self.pythonContext = {};
        break;
      case 'fetchFiles':
        for(const { url, path } of data.fileURLs) {
          const response = await fetch(url, { cache: "no-store" });
          const content = await response.text();
          self.pyodide.FS.writeFile(path, content, { encoding: "utf8" });
        }
        result = JSON.stringify({ filesFetched: true });
        break;
      case 'writeFiles':
        for(const { content, path } of data.fileContents) {
          self.pyodide.FS.writeFile(path, content, {encoding: "utf8"});
        }
        result = JSON.stringify({ filesWritten: true });
    }
    self.postMessage({ result });
  } catch (e) {
    console.log("WORKER ERROR")
    console.log(e.message)
    console.log(e.stack)
    self.postMessage(JSON.stringify({ error: e.message + "\n" + e.stack }));
  }
};
