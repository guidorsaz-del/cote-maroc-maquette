// Détoure une personne avec le masque « accurate » de Vision (bords de cheveux plus doux que le masque d'instance).
// Usage : detourer-personne entrée.jpg sortie.png
import Foundation
import Vision
import CoreImage

let args = CommandLine.arguments
guard args.count == 3 else { FileHandle.standardError.write("usage: detourer-personne entree sortie\n".data(using: .utf8)!); exit(64) }
let entree = URL(fileURLWithPath: args[1]), sortie = URL(fileURLWithPath: args[2])
guard let image = CIImage(contentsOf: entree, options: [.applyOrientationProperty: true]) else { FileHandle.standardError.write("image illisible\n".data(using: .utf8)!); exit(1) }
let requete = VNGeneratePersonSegmentationRequest()
requete.qualityLevel = .accurate
requete.outputPixelFormat = kCVPixelFormatType_OneComponent8
let gestionnaire = VNImageRequestHandler(ciImage: image, options: [:])
do {
  try gestionnaire.perform([requete])
  guard let resultat = requete.results?.first else { FileHandle.standardError.write("aucune personne détectée\n".data(using: .utf8)!); exit(2) }
  let masque = CIImage(cvPixelBuffer: resultat.pixelBuffer)
  let sx = image.extent.width / masque.extent.width, sy = image.extent.height / masque.extent.height
  let masqueEchelle = masque.transformed(by: CGAffineTransform(scaleX: sx, y: sy))
  let fond = CIImage(color: CIColor(red: 0, green: 0, blue: 0, alpha: 0)).cropped(to: image.extent)
  guard let filtre = CIFilter(name: "CIBlendWithMask") else { exit(3) }
  filtre.setValue(image, forKey: kCIInputImageKey)
  filtre.setValue(fond, forKey: kCIInputBackgroundImageKey)
  filtre.setValue(masqueEchelle, forKey: kCIInputMaskImageKey)
  guard let detouree = filtre.outputImage else { exit(3) }
  let contexte = CIContext()
  guard let png = contexte.pngRepresentation(of: detouree, format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!) else { exit(3) }
  try png.write(to: sortie)
  print("masque \(Int(masque.extent.width))x\(Int(masque.extent.height)) -> image \(Int(image.extent.width))x\(Int(image.extent.height))")
} catch { FileHandle.standardError.write("erreur : \(error)\n".data(using: .utf8)!); exit(4) }
