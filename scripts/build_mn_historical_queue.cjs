#!/usr/bin/env node
/* Public original-index rows in stdin -> deterministic metadata-only review queue JSON.
 * This script does not call a service, fetch PDFs, or update an agency dossier.
 */
'use strict';
const fs=require('node:fs'),H=require('../mn-audit-candidates.js');
const input=fs.readFileSync(0,'utf8');
if(input.length>800000)throw Error('Unbounded state index payload');
const data=JSON.parse(input);
const result=H.plan(data.rows,data.manifest);
process.stdout.write(JSON.stringify(result)+'\n');
