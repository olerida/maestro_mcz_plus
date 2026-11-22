import AppKit
import SwiftUI

struct Reading: Decodable, Identifiable {
    let id: String
    let label: String
    let value: String
}

struct StoveSnapshot: Decodable {
    let telemetry: [Reading]
    let recipes: [Reading]

    static func load() -> Self? {
        guard let url = Bundle.main.url(forResource: "sample", withExtension: "json"),
              let data = try? Data(contentsOf: url) else {
            return nil
        }
        return try? JSONDecoder().decode(Self.self, from: data)
    }
}

struct MaestroPreview: App {
    var body: some Scene {
        Window("Maestro MCZ Plus · Vista previa para macOS", id: "preview") {
            PreviewView(snapshot: StoveSnapshot.load())
                .frame(minWidth: 520, minHeight: 550)
        }
        .defaultSize(width: 620, height: 610)
    }
}

struct PreviewView: View {
    let snapshot: StoveSnapshot?

    var body: some View {
        VStack(alignment: .leading, spacing: 22) {
            VStack(alignment: .leading, spacing: 6) {
                Label("Maestro MCZ Plus", systemImage: "flame.fill")
                    .font(.largeTitle.bold())
                Text("Demostración de la integración para Home Assistant con datos simulados.")
                    .foregroundStyle(.secondary)
            }

            if let snapshot {
                readings("Datos de funcionamiento", snapshot.telemetry)
                readings("Recetas", snapshot.recipes)
            } else {
                Text("No se han podido cargar los datos de ejemplo.")
            }
            Spacer(minLength: 0)
        }
        .padding(28)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .background(Color(nsColor: .windowBackgroundColor))
    }

    private func readings(_ title: String, _ readings: [Reading]) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(title)
                .font(.headline)
                .accessibilityAddTraits(.isHeader)
            ForEach(readings) { reading in
                Divider()
                HStack(alignment: .firstTextBaseline) {
                    Text(reading.label)
                    Spacer()
                    Text(reading.value)
                        .monospacedDigit()
                }
                .accessibilityElement(children: .combine)
            }
        }
    }
}

@main
struct MaestroPreviewCommand {
    @MainActor
    static func main() {
        let arguments = CommandLine.arguments
        guard arguments.dropFirst().first == "--screenshot" else {
            MaestroPreview.main()
            return
        }
        guard arguments.count == 3, let snapshot = StoveSnapshot.load() else {
            fail("Se necesitan los datos de ejemplo y una ruta de salida PNG.")
        }
        let view = PreviewView(snapshot: snapshot).frame(width: 620, height: 610)
        let renderer = ImageRenderer(content: view)
        renderer.scale = 2
        guard let image = renderer.cgImage,
              let png = NSBitmapImageRep(cgImage: image).representation(using: .png, properties: [:]) else {
            fail("No se ha podido renderizar la vista previa.")
        }
        do {
            try png.write(to: URL(fileURLWithPath: arguments[2]), options: .atomic)
        } catch {
            fail(error.localizedDescription)
        }
    }

    private static func fail(_ message: String) -> Never {
        FileHandle.standardError.write(Data((message + "\n").utf8))
        exit(EXIT_FAILURE)
    }
}
