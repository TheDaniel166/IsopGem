import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface PyreInput {
    workspace_root: string;
    target_path: string;
    reason: string;
}

export interface PyreResult {
    target: string;
    archived_to: string;
    reason: string;
    status: string;
}

export class PyreTool implements vscode.LanguageModelTool<PyreInput> {
    public readonly name = 'sophia_pyre';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<PyreInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, target_path, reason } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/pyre_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                target_path,
                reason
            ]);

            if (stderr) {
                console.error('Pyre stderr:', stderr);
            }

            const result: PyreResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Pyre ritual failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<PyreInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Archiving to Pyre: ${options.input.target_path}`
        };
    }
}
