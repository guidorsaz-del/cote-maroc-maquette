// Détoure le sujet principal d'une photo avec Vision (macOS 14+). Usage : detourer entrée.png sortie.png
import Foundation
import Vision
import CoreImage

let args = CommandLine.arguments
guard args.count == 3 else { FileHandle.standardError.write("usage: detourer entree sortie\n".data(using: .utf8)!); exit(64) }
let entree = URL(fileURLWithPath: args[1]), sortie = URL(fileURLWithPath: args[2])
guard let image = CIImage(contentsOf: entree, options: [.applyOrientationProperty: true]) else { FileHandle.standardError.write("image illisible\n".data(using: .utf8)!); exit(1) }
let requete = VNGenerateForegroundInstanceMaskRequest()
let gestionnaire = VNImageRequestHandler(ciImage: image, options: [:])
do {
  try gestionnaire.perform([requete])
  guard let resultat = requete.results?.first else { FileHandle.standardError.write("aucun sujet détecté\n".data(using: .utf8)!); exit(2) }
  let tampon = try resultat.generateMaskedImage(ofInstances: resultat.allInstances, from: gestionnaire, croppedToInstancesExtent: false)
  let detouree = CIImage(cvPixelBuffer: tampon)
  let contexte = CIContext()
  guard let png = contexte.pngRepresentation(of: detouree, format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!) else { exit(3) }
  try png.write(to: sortie)
  print("détourage ok : \(Int(detouree.extent.width))x\(Int(detouree.extent.height)), \(resultat.allInstances.count) sujet(s)")
} catch { FileHandle.standardError.write("erreur : \(error)\n".data(using: .utf8)!); exit(4) }
