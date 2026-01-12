import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface DreamInput {
    insight: string;
    category?: string;
    workspace_root: string;
}

export interface DreamOutput {
    success: boolean;
    timestamp: string;
    message: string;
}

export class DreamTool implements vscode.LanguageModelTool<DreamInput> {
    public readonly name = 'sophia_dream';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<DreamInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { insight, category = 'other', workspace_root } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/dream_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                insight,
                category
            ]);

            if (stderr) {
                console.error('Dream stderr:', stderr);
            }

            const result: DreamOutput = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Dream failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<DreamInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: 'Recording creative insight...'
        };
    }
}
