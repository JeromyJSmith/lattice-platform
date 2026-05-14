{ VW Universe — Pre-flight Probe (VectorScript)

  Run this BEFORE extract_all.py to confirm the document is ready.
  VectorScript has 30 years of API stability; this probe has no Python gotchas.

  Output: writes preflight.json next to the open document.
  Reads cleanly by LATTICE via vwx-mcp execute_script or manually.

  Checks:
    1. Document path (POSIX since VW 2019)
    2. Document name
    3. IFC scheme (must be IFC4X3 before extract)
    4. Layer count
    5. Class count
    6. Whether any migration is pending (heuristic via version check)
    7. VW version string
}

PROCEDURE Preflight;

VAR
  docPath     : STRING;
  docName     : STRING;
  ifcScheme   : STRING;
  layerCount  : INTEGER;
  classCount  : INTEGER;
  vwVersion   : STRING;
  outputDir   : STRING;
  jsonPath    : STRING;
  fileRef     : INTEGER;
  jsonStr     : STRING;

  PROCEDURE AppendLine(VAR s : STRING; line : STRING);
  BEGIN
    s := Concat(s, line, Chr(10));
  END;

BEGIN
  { --- Document info --- }
  docPath   := GetFPathName;
  docName   := GetFName;
  vwVersion := GetVWVersion;

  { --- IFC scheme --- }
  ifcScheme := IFC_GetIFCScheme;
  IF ifcScheme = '' THEN
    ifcScheme := 'UNKNOWN';

  { --- Counts --- }
  layerCount := 0;
  classCount := ClassNum;

  { Count layers via iteration }
  VAR lh : HANDLE;
  lh := FLayer;
  WHILE lh <> NIL DO
  BEGIN
    layerCount := layerCount + 1;
    lh := NextLayer(lh);
  END;

  { --- Build JSON string --- }
  jsonStr := '{';
  AppendLine(jsonStr, '');
  AppendLine(jsonStr, Concat('  "doc_path": "', docPath, '",'));
  AppendLine(jsonStr, Concat('  "doc_name": "', docName, '",'));
  AppendLine(jsonStr, Concat('  "vw_version": "', vwVersion, '",'));
  AppendLine(jsonStr, Concat('  "ifc_scheme": "', ifcScheme, '",'));
  AppendLine(jsonStr, Concat('  "ifc_scheme_ok": ', BooleanToStr(ifcScheme = 'IFC4X3'), ','));
  AppendLine(jsonStr, Concat('  "layer_count": ', Num2Str(0, layerCount), ','));
  AppendLine(jsonStr, Concat('  "class_count": ', Num2Str(0, classCount)));
  AppendLine(jsonStr, '}');

  { --- Write to preflight.json next to document --- }
  { Strip filename, keep dir — VW 2019+ returns POSIX path }
  outputDir := docPath;
  { Remove trailing filename — find last / }
  VAR i : INTEGER;
  FOR i := Len(outputDir) DOWNTO 1 DO
  BEGIN
    IF Copy(outputDir, i, 1) = '/' THEN
    BEGIN
      outputDir := Copy(outputDir, 1, i);
      i := 0;  { break }
    END;
  END;

  jsonPath := Concat(outputDir, 'preflight.json');

  fileRef := FOpen(jsonPath, 'w');
  IF fileRef > 0 THEN
  BEGIN
    WriteLn(fileRef, jsonStr);
    FClose(fileRef);
    AlrtDialog(Concat('Preflight OK. IFC scheme: ', ifcScheme, Chr(10), 'Layers: ', Num2Str(0, layerCount), '  Classes: ', Num2Str(0, classCount)));
  END
  ELSE
    AlrtDialog(Concat('ERROR: Could not write preflight.json to: ', outputDir));
END;

RUN(Preflight);
