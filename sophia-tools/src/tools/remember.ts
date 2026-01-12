import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface RememberInput {
    query: string;
    workspace_root: string;
    max_results?: number;
}

export interface MemoryEntry {
    source: string;
    date: string;
    content: string;
    relevance: number;
}

export interface RememberOutput {
    query: string;
    results: MemoryEntry[];
    total_found: number;
}

export class RememberTool implements vscode.LanguageModelTool<RememberInput> {
    public readonly name = 'sophia_remember';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<RememberInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { query, workspace_root, max_results = 5 } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/remember_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                query,
                String(max_results)
            ]);

            if (stderr) {
                console.error('Remember stderr:', stderr);
            }

            const result: RememberOutput = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Remember failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<RememberInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Searching memory for: ${options.input.query}`
        };
    }
}
