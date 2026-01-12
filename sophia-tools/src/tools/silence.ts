import * as vscode from 'vscode';
import * as path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export interface SilenceInput {
    workspace_root: string;
    target?: string;
    threshold?: string;
}

export interface CognitiveMetrics {
    file: string;
    concept_density: number;
    indirection_depth: number;
    cognitive_jumps: number;
    symbol_reuse_conflicts: number;
    understanding_burden: string;
}

export interface SilenceResult {
    target: string;
    total_files_analyzed: number;
    hostile_files: CognitiveMetrics[];
    severe_files: CognitiveMetrics[];
    moderate_files: CognitiveMetrics[];
    cognitive_hotspots: string[];
    verdicts: string[];
}

export class SilenceTool implements vscode.LanguageModelTool<SilenceInput> {
    public readonly name = 'sophia_silence';
    public readonly tags = ['sophia-tools'];

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<SilenceInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const { workspace_root, target = 'src', threshold = 'medium' } = options.input;
        
        try {
            const pythonScript = path.join(__dirname, '../../python/silence_bridge.py');
            const { stdout, stderr } = await execFileAsync('python3', [
                pythonScript,
                workspace_root,
                target,
                threshold
            ]);

            if (stderr) {
                console.error('Silence stderr:', stderr);
            }

            const result: SilenceResult = JSON.parse(stdout);

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
                        JSON.stringify({ error: `Silence failed: ${errorMessage}` }, null, 2)
                    )
                ]
            };
        }
    }

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<SilenceInput>,
        token: vscode.CancellationToken
    ): Promise<vscode.PreparedToolInvocation> {
        return {
            invocationMessage: `Measuring cognitive load: ${options.input.target || 'src'}`
        };
    }
}
