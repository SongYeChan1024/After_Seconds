import {Workbook} from '@oai/artifact-tool';
console.log(Workbook.create().help('workbook.calculationMode',{include:'index,examples,notes',maxChars:2000}).ndjson);
