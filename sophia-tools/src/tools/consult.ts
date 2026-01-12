import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface ConsultInput {
    query: string;
    scope?: string;
    workspace_root: string;
}

export interface CovenantResult {
    source: string;
    section: string;
    content: string;
    relevance: number;
}

export interface ConsultOutput {
    query: string;
    scope: string;
    results: CovenantResult[];
    total_found: number;
}

export class ConsultTool implements vscode.LanguageModelTool<ConsultInput> {
    public readonly name = 'sophia_consult';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<ConsultInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { query, scope = 'all', workspace_root } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/consult_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                query,
                scope
            ]);

            if (stderr) {
                console.error('Consult stderr:', stderr);
            }

            const result: ConsultOutput = JSON.parse(stdout);

            return {
                content: [
                    new vscode.LanguageModelTextPart(JSON.stringify(result, null, 2))
                ]
            };
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : String(error);
            return {
                content: [
                    new vscode.LanguageModelTextPart(
                        JSON.stringify({ error: `Consult failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<ConsultInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Consulting covenant for: ${options.input.query}`
        };
    }
}
