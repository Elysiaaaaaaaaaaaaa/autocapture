#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const IMAGE_EXTENSIONS = new Set([".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"]);
const NORMAL_NAMES = new Set(["normal", "正常"]);
const TITLE_FILL = "#1F4E78";
const HEADER_FILL = "#5B9BD5";
const GROUP_FILL = "#D9EAF7";
const DETAIL_FILL = "#FFF2CC";
const BORDER_COLOR = "#B4C6E7";

function compareText(left, right) {
  return String(left).localeCompare(String(right), "zh-CN", { numeric: true });
}

function isImageFile(name) {
  return IMAGE_EXTENSIONS.has(path.extname(name).toLowerCase());
}

function isTopViewDirectory(name) {
  return /^(?:top|view[_-]?top|overview[_-]?top)(?:[_-]?\d+(?:[-_]\d+)*)?$/i.test(name);
}

function parsePointView(directoryName) {
  const separator = directoryName.lastIndexOf("-");
  if (separator <= 0 || separator === directoryName.length - 1) {
    return { point: directoryName || "未识别", view: "未识别", parseStatus: "点位目录缺少末尾视角编号" };
  }
  return {
    point: directoryName.slice(0, separator),
    view: directoryName.slice(separator + 1),
    parseStatus: "已解析",
  };
}

function normalizeImage(relativeParts) {
  const target = relativeParts[0];
  const major = relativeParts[1];
  if (!target || !major) return null;

  const isNormal = NORMAL_NAMES.has(major.toLowerCase());
  const minor = isNormal ? "—" : relativeParts[2];
  const shotIndex = isNormal ? 2 : 3;
  const shotDirectory = relativeParts[shotIndex];

  if (!shotDirectory) {
    return {
      key: relativeParts.join("\u0001"),
      target,
      major,
      minor: minor ?? "未识别",
      point: "未识别",
      view: "未识别",
      directImageCount: 0,
      nestedImageCount: 0,
      imageCount: 0,
      parseStatus: isNormal ? "缺少点位目录" : "缺少异常小类或点位目录",
      relativePath: relativeParts.join("/"),
      nested: false,
    };
  }

  const parsed = parsePointView(shotDirectory);
  const shotParts = relativeParts.slice(0, shotIndex + 1);
  return {
    key: shotParts.join("\u0001"),
    target,
    major,
    minor: minor ?? "未识别",
    point: parsed.point,
    view: parsed.view,
    directImageCount: 0,
    nestedImageCount: 0,
    imageCount: 0,
    parseStatus: minor ? parsed.parseStatus : "缺少异常小类",
    relativePath: shotParts.join("/"),
    nested: relativeParts.length > shotIndex + 1,
  };
}

export async function scanDataset(rootPath) {
  const absoluteRoot = path.resolve(rootPath);
  const rootStats = await fs.stat(absoluteRoot).catch(() => null);
  if (!rootStats?.isDirectory()) {
    throw new Error(`数据集目录不存在或不是目录：${absoluteRoot}`);
  }

  const recordsByKey = new Map();

  async function walk(currentPath) {
    const entries = await fs.readdir(currentPath, { withFileTypes: true });
    for (const entry of entries) {
      const entryPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        await walk(entryPath);
        continue;
      }
      if (!entry.isFile() || !isImageFile(entry.name)) continue;

      const relativeDirectory = path.relative(absoluteRoot, currentPath);
      const relativeParts = relativeDirectory.split(path.sep).filter(Boolean);
      const isNormal = relativeParts[1] && NORMAL_NAMES.has(relativeParts[1].toLowerCase());
      const shotIndex = isNormal ? 2 : 3;
      if (relativeParts.slice(shotIndex).some(isTopViewDirectory)) continue;
      const image = normalizeImage(relativeParts);
      if (!image) continue;

      const record = recordsByKey.get(image.key) ?? image;
      record.imageCount += 1;
      if (image.nested) record.nestedImageCount += 1;
      else record.directImageCount += 1;
      recordsByKey.set(image.key, record);
    }
  }

  await walk(absoluteRoot);
  return [...recordsByKey.values()]
    .map(({ key, nested, ...record }) => record)
    .sort((left, right) =>
      compareText(left.target, right.target) ||
      compareText(left.major, right.major) ||
      compareText(left.minor, right.minor) ||
      compareText(left.point, right.point) ||
      compareText(left.view, right.view),
    );
}

function hierarchyKey(...parts) {
  return parts.join("\u0001");
}

function aggregatePoints(records) {
  const groups = new Map();
  for (const record of records) {
    const key = hierarchyKey(record.target, record.major, record.minor, record.point);
    const group = groups.get(key) ?? {
      target: record.target,
      major: record.major,
      minor: record.minor,
      point: record.point,
      views: [],
    };
    group.views.push(record);
    groups.set(key, group);
  }

  return [...groups.values()]
    .map((group) => ({
      ...group,
      views: group.views.sort((left, right) => compareText(left.view, right.view)),
      viewCount: group.views.length,
      imageTotal: group.views.reduce((total, view) => total + view.imageCount, 0),
    }))
    .sort((left, right) =>
      compareText(left.target, right.target) ||
      compareText(left.major, right.major) ||
      compareText(left.minor, right.minor) ||
      compareText(left.point, right.point),
    );
}

function aggregateHierarchyTotals(summaryPoints) {
  const pointTotals = new Map();
  const minorTotals = new Map();
  const majorTotals = new Map();
  for (const group of summaryPoints) {
    pointTotals.set(hierarchyKey(group.target, group.major, group.minor, group.point), group.imageTotal);
    const minorKey = hierarchyKey(group.target, group.major, group.minor);
    minorTotals.set(minorKey, (minorTotals.get(minorKey) ?? 0) + group.imageTotal);
    const majorKey = hierarchyKey(group.target, group.major);
    majorTotals.set(majorKey, (majorTotals.get(majorKey) ?? 0) + group.imageTotal);
  }
  return { pointTotals, minorTotals, majorTotals };
}

function columnName(index) {
  let value = index;
  let result = "";
  while (value > 0) {
    result = String.fromCharCode(65 + ((value - 1) % 26)) + result;
    value = Math.floor((value - 1) / 26);
  }
  return result;
}

function setColumnWidths(sheet, widths) {
  widths.forEach((width, index) => {
    const column = columnName(index + 1);
    sheet.getRange(`${column}:${column}`).format.columnWidth = width;
  });
}

async function styleSummarySheet(sheet, rowCount, datasetLabel) {
  const lastRow = rowCount + 4;
  sheet.showGridLines = false;
  await sheet.mergeCells("A1:H1");
  sheet.getRange("A1").values = [[`${datasetLabel} 数据集统计表`]];
  sheet.getRange("A1:H1").format = {
    fill: TITLE_FILL,
    font: { bold: true, color: "#FFFFFF", size: 16 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    rowHeight: 30,
  };

  await sheet.mergeCells("A2:H2");
  sheet.getRange("A2").values = [["统计规则：图片归属到最近的“点位-视角”目录；top* / view_top_* 俯视子目录中的图片不计入统计。名称后的 *数字为对应层级图片总数。"]];
  sheet.getRange("A2:H2").format = {
    fill: "#EAF2F8",
    font: { color: "#3F3F3F", italic: true, size: 10 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
    wrapText: true,
    rowHeight: 26,
  };

  sheet.getRange("A4:H4").values = [[
    "目标种类", "异常大类", "异常小类", "点位", "视角×图片数", "视角数", "平均图片/视角", "图片总数",
  ]];
  sheet.getRange("A4:H4").format = {
    fill: HEADER_FILL,
    font: { bold: true, color: "#FFFFFF", size: 11 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: BORDER_COLOR },
    rowHeight: 30,
  };

  if (rowCount > 0) {
    sheet.getRange(`A5:D${lastRow}`).format = {
      fill: GROUP_FILL,
      verticalAlignment: "center",
      wrapText: true,
      borders: { preset: "all", style: "thin", color: BORDER_COLOR },
    };
    sheet.getRange(`E5:H${lastRow}`).format = {
      fill: DETAIL_FILL,
      verticalAlignment: "center",
      wrapText: true,
      borders: { preset: "all", style: "thin", color: BORDER_COLOR },
    };
    sheet.getRange(`F5:H${lastRow}`).format.horizontalAlignment = "center";
    sheet.getRange(`F5:F${lastRow}`).format.numberFormat = "#,##0";
    sheet.getRange(`G5:G${lastRow}`).format.numberFormat = "0.0";
    sheet.getRange(`H5:H${lastRow}`).format.numberFormat = "#,##0";
    sheet.getRange(`A5:H${lastRow}`).format.rowHeight = 25;
  }
  setColumnWidths(sheet, [23, 25, 28, 36, 58, 11, 16, 12]);
  sheet.freezePanes.freezeRows(4);
  sheet.freezePanes.freezeColumns(4);
}

async function styleDetailSheet(sheet, rowCount) {
  const lastRow = rowCount + 3;
  sheet.showGridLines = false;
  await sheet.mergeCells("A1:J1");
  sheet.getRange("A1").values = [["视角明细（每行一个点位-视角目录）"]];
  sheet.getRange("A1:J1").format = {
    fill: TITLE_FILL,
    font: { bold: true, color: "#FFFFFF", size: 15 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    rowHeight: 28,
  };
  sheet.getRange("A3:J3").values = [[
    "目标种类", "异常大类", "异常小类", "点位", "视角编号", "点位目录图片", "相机子目录图片", "图片总数", "解析状态", "相对目录",
  ]];
  sheet.getRange("A3:J3").format = {
    fill: HEADER_FILL,
    font: { bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: BORDER_COLOR },
    rowHeight: 30,
  };
  if (rowCount > 0) {
    sheet.getRange(`A4:J${lastRow}`).format = {
      verticalAlignment: "center",
      wrapText: true,
      borders: { preset: "all", style: "thin", color: "#D9E2F3" },
      rowHeight: 22,
    };
    sheet.getRange(`E4:E${lastRow}`).format.numberFormat = "@";
    sheet.getRange(`F4:H${lastRow}`).format.numberFormat = "#,##0";
    sheet.getRange(`F4:H${lastRow}`).format.horizontalAlignment = "center";
    sheet.tables.add(`A3:J${lastRow}`, true, "DatasetViewDetailTable");
  }
  setColumnWidths(sheet, [22, 23, 26, 34, 12, 14, 15, 12, 24, 72]);
  sheet.freezePanes.freezeRows(3);
}

export async function buildWorkbook(records, outputPath, options = {}) {
  const summaryPoints = aggregatePoints(records);
  const { pointTotals, minorTotals, majorTotals } = aggregateHierarchyTotals(summaryPoints);
  const workbook = Workbook.create();
  const summarySheet = workbook.worksheets.add("数据总览");
  const detailSheet = workbook.worksheets.add("视角明细");

  await styleSummarySheet(summarySheet, summaryPoints.length, options.datasetLabel ?? "dataset");
  const summaryValues = summaryPoints.map((group, index) => {
    const previous = summaryPoints[index - 1];
    const sameTarget = previous?.target === group.target;
    const sameMajor = sameTarget && previous.major === group.major;
    const sameMinor = sameMajor && previous.minor === group.minor;
    return [
      sameTarget ? "" : group.target,
      sameMajor ? "" : `${group.major}*${majorTotals.get(hierarchyKey(group.target, group.major))}`,
      sameMinor ? "" : group.minor === "—" ? "—" : `${group.minor}*${minorTotals.get(hierarchyKey(group.target, group.major, group.minor))}`,
      `${group.point}*${pointTotals.get(hierarchyKey(group.target, group.major, group.minor, group.point))}`,
      group.views.map((view) => `${view.view}×${view.imageCount}`).join("；"),
      group.viewCount,
      null,
      group.imageTotal,
    ];
  });
  if (summaryValues.length > 0) {
    const lastSummaryRow = summaryValues.length + 4;
    summarySheet.getRange(`A5:H${lastSummaryRow}`).values = summaryValues;
    summarySheet.getRange("G5").formulas = [["=IFERROR(H5/F5,0)"]];
    summarySheet.getRange(`G5:G${lastSummaryRow}`).fillDown();
  }

  await styleDetailSheet(detailSheet, records.length);
  if (records.length > 0) {
    detailSheet.getRange(`A4:J${records.length + 3}`).values = records.map((record) => [
      record.target,
      record.major,
      record.minor,
      record.point,
      record.view === "未识别" ? record.view : `视角${record.view}`,
      record.directImageCount,
      record.nestedImageCount,
      record.imageCount,
      record.parseStatus,
      record.relativePath,
    ]);
  }

  await fs.mkdir(path.dirname(path.resolve(outputPath)), { recursive: true });
  const exported = await SpreadsheetFile.exportXlsx(workbook);
  await exported.save(outputPath);
  return { workbook, summaryPoints };
}

export async function validateWorkbook(records, outputPath) {
  const expectedImages = records.reduce((total, record) => total + record.imageCount, 0);
  const blob = await FileBlob.load(outputPath);
  const workbook = await SpreadsheetFile.importXlsx(blob);
  const summarySheet = workbook.worksheets.getItem("数据总览");
  const detailSheet = workbook.worksheets.getItem("视角明细");

  const detailValues = await detailSheet.getRange(`H4:H${records.length + 3}`).values;
  const detailImages = detailValues.reduce((total, [value]) => total + Number(value ?? 0), 0);
  if (detailImages !== expectedImages) {
    throw new Error(`明细图片总数校验失败：源数据 ${expectedImages}，工作簿 ${detailImages}`);
  }

  const summaryPoints = aggregatePoints(records);
  const summaryValues = await summarySheet.getRange(`H5:H${summaryPoints.length + 4}`).values;
  const summaryImages = summaryValues.reduce((total, [value]) => total + Number(value ?? 0), 0);
  if (summaryImages !== expectedImages) {
    throw new Error(`总览图片总数校验失败：源数据 ${expectedImages}，工作簿 ${summaryImages}`);
  }

  const formulaErrors = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 100 },
    summary: "formula error scan",
    maxChars: 3000,
  });
  return { workbook, expectedImages, summaryPoints, formulaErrors };
}

function getFlag(args, flag) {
  const index = args.indexOf(flag);
  return index === -1 ? undefined : args[index + 1];
}

function requireFlagValue(args, flag) {
  const index = args.indexOf(flag);
  if (index !== -1 && (!args[index + 1] || args[index + 1].startsWith("--"))) {
    throw new Error(`${flag} 后必须提供路径或名称`);
  }
}

function printUsage() {
  console.log(`用法：
  node generate_dataset_table.mjs [选项]

选项：
  --input <目录>   数据集根目录
                   默认：DATASET_ROOT 环境变量，或
                   /home/qy/dataset-202607/quality test/empty_container
  --output <文件>  xlsx 输出路径
                   默认：项目 outputs/<数据集名>_数据集统计表.xlsx
  --name <名称>    表格标题中的数据集名称，默认使用输入目录名
  -h, --help       显示帮助
`);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes("--help") || args.includes("-h")) {
    printUsage();
    return;
  }
  requireFlagValue(args, "--input");
  requireFlagValue(args, "--output");
  requireFlagValue(args, "--name");

  const scriptRoot = path.dirname(fileURLToPath(import.meta.url));
  const defaultInput = process.env.DATASET_ROOT ?? "/home/qy/dataset-202607/quality test/empty_container";
  const inputPath = path.resolve(getFlag(args, "--input") ?? defaultInput);
  const datasetName = getFlag(args, "--name") ?? path.basename(inputPath);
  const outputPath = path.resolve(
    getFlag(args, "--output") ?? path.join(scriptRoot, "outputs", `${datasetName}_数据集统计表.xlsx`),
  );

  const records = await scanDataset(inputPath);
  if (records.length === 0) {
    throw new Error(`未在 ${inputPath} 中找到可统计的图片文件`);
  }
  await buildWorkbook(records, outputPath, { datasetLabel: datasetName });
  const validation = await validateWorkbook(records, outputPath);
  console.log(JSON.stringify({
    input: inputPath,
    output: outputPath,
    imageCount: validation.expectedImages,
    viewRecordCount: records.length,
    pointRecordCount: validation.summaryPoints.length,
    parseWarnings: records.filter((record) => record.parseStatus !== "已解析").length,
    formulaErrors: validation.formulaErrors.ndjson,
  }, null, 2));
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await main();
}
