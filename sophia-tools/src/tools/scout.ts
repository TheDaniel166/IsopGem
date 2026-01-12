import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface ScoutInput {
    workspace_root: string;
    scope?: string;
}

export interface ScoutResult {
    pillars: string[];
    missing_inits: string[];
    orphaned_files: string[];
    structure_issues: string[];
}

export class ScoutTool implements vscode.LanguageModelTool<ScoutInput> {
    public readonly name = 'sophia_scout';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<ScoutInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, scope = 'pillars' } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/scout_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                scope
            ]);

            if (stderr) {
                console.error('Scout stderr:', stderr);
            }

            const result: ScoutResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Scout failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<ScoutInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Performing Scout Ritual on: ${options.input.scope}`
        };
    }
}
