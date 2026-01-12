import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface GenesisInput {
    workspace_root: string;
    pillar_name: string;
    description?: string;
}

export interface GenesisResult {
    pillar_name: string;
    created_directories: string[];
    created_files: string[];
    status: string;
}

export class GenesisTool implements vscode.LanguageModelTool<GenesisInput> {
    public readonly name = 'sophia_genesis';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<GenesisInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, pillar_name, description = '' } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/genesis_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                pillar_name,
                description
            ]);

            if (stderr) {
                console.error('Genesis stderr:', stderr);
            }

            const result: GenesisResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Genesis failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<GenesisInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Creating new pillar: ${options.input.pillar_name}`
        };
    }
}
